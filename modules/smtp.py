import os
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from modules import gptWeather
from modules import db
from .logger import logger
import time

# SMTP Configuration
imap_host = os.getenv('IMAP_HOST', 'imap.gmail.com')
smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
smtp_username = os.getenv('SMTP_USERNAME')
smtp_password = os.getenv('SMTP_PASSWORD')
mail_rate_limit = int(os.getenv('RATE_LIMIT', '30'))

# Handling allowed_domains as a list
allowed_domains_string = os.getenv('ALLOWED_DOMAINS')
allowed_domains = [domain.strip() for domain in allowed_domains_string.split(',')]

# Open AI Configuration
oai_api_key = os.getenv('OAI_API_KEY')
oai_model = os.getenv('OAI_MODEL', 'gpt-3.5-turbo-0125')
oai_max_tokens = int(os.getenv('OAI_MAX_TOKENS', '50'))

# Open Weather Map Configuration
weather_api_key = os.getenv('WEATHER_API_KEY')

def move_to_label(mail, mail_id, folder_name):
    # Moving emails in standard IMAP (MXroute does not support Gmail labels)
    result, _ = mail.copy(mail_id, folder_name)  # Copy to another folder
    if result == 'OK':
        mail.store(mail_id, '+FLAGS', '\\Deleted')  # Mark the original email as deleted
        mail.expunge()  # Permanently remove email marked as deleted
    logger.info(f"Moved mail ID {mail_id} to {folder_name}.")

# Helper to extract email body
def extract_body(message):
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return message.get_payload(decode=True).decode('utf-8')
    return None

# Get emails with subject weather that are unread and parse data
def fetch_emails():
    logger.info("Starting email fetch process...")
    try:
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(smtp_username, smtp_password)
        mail.select('Inbox')
        
        status, messages = mail.search(None, '(SUBJECT "weather" UNSEEN)')
        if status != 'OK':
            logger.error("Failed to search for emails.")
            return
        
        messages = messages[0].split()
        logger.info(f"Found {len(messages)} messages with specified subject and unseen status.")

        for mail_id in messages:
            status, data = mail.fetch(mail_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"Failed to fetch email with ID {mail_id}.")
                continue

            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    from_field = message['from']
                    domain = from_field.split('@')[-1].strip('>')
                    logger.info(f"Email from: {from_field}")
                    logger.info(f"Domain extracted: {domain}")
                    
                    if '*' in allowed_domains or domain in allowed_domains:
                        logger.info("Handling email from allowed domain...")
                        handle_email(message)
                        move_to_label(mail, mail_id, 'Processed')
                    else:
                        logger.warning(f"Domain {domain} not in allowed list.")
                        move_to_label(mail, mail_id, 'NotAction')

    except Exception as e:
        logger.error(f"An error occurred during email fetching: {str(e)}")
    finally:
        try:
            mail.close()
            mail.logout()
        except:
            logger.error("Failed to close or logout from IMAP session.")
            
    logger.info("Email fetch process completed.")

# Determine report type and send to handle_weather_report
def handle_email(message):
    from_field = message['from']
    current_time = time.time()
    last_request_time = db.get_last_request_time(from_field)

    # Check if the last request was less than 30 seconds ago
    if last_request_time is not None and (current_time - last_request_time < mail_rate_limit):
        logger.warning(f"Discarding request from {from_field} due to high frequency.")
        return  # Skip processing this request

    # Update the last request time in the database
    db.update_last_request_time(from_field, current_time)

    subject = message['subject']
    logger.info(f"Handling email with subject: {subject}")

    if subject.lower().startswith('weather:'):
        report_type = subject.split(':')[1].strip()  # Assumes the subject is in the form 'weather:type'
        if report_type in ['daily', 'current', 'hourly']:
            handle_weather_report(message, report_type)
        else:
            logger.error(f"Invalid weather report type: {report_type}")
    else:
        logger.info(f"Subject {subject} did not start with 'weather:'. Ignored.")

# Call GPT functions with paresed email
def handle_weather_report(message, report_type):
    body = extract_body(message)
    if body is None:
        logger.error("Failed to extract body from the message.")
        send_error_email(message['from'], "Failed to extract the email body.")
        return
    
    logger.info(f"Extracted body: {body}")
    try:
        location_data = body.strip()
        forecast = gptWeather.generate_weather_report(location_content=location_data, oai_api_key=oai_api_key, oai_max_tokens=oai_max_tokens, weather_api_key=weather_api_key, type=report_type)
        if forecast is None:
            raise ValueError("Generated forecast is None.")
        send_forecast_email(message['from'], forecast)
    except Exception as e:
        logger.error(f"Failed to generate a valid forecast for {location_data} due to: {str(e)}")
        send_error_email(message['from'], f"Failed to generate the weather report for: {location_data} |  Error: {str(e)}")

# Send the forecast back to the requesting user
def send_forecast_email(recipient, forecast):
    if forecast is None or recipient is None:
        logger.error("Invalid forecast or recipient. Email not sent.")
        return

    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = recipient
    message['Subject'] = 'Your Requested Weather Forecast'

    message.attach(MIMEText(forecast, 'plain'))

    server = smtplib.SMTP(smtp_host, 587)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, recipient, message.as_string())
    server.quit()
    logger.info(f"Forecast sent to {recipient}.")

# Send error to the user if error occurs
def send_error_email(recipient, error_message):
    if recipient is None:
        logger.error("Recipient is None. Error email not sent.")
        return
    
    message = MIMEMultipart()
    message['From'] = smtp_username
    message['To'] = recipient
    message['Subject'] = 'Error Processing Your Weather Request'
    message.attach(MIMEText(f"There was an error processing your weather request: {error_message}", 'plain'))

    server = smtplib.SMTP(smtp_host, 587)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, recipient, message.as_string())
    server.quit()
    logger.info(f"Error notification sent to {recipient}.")
