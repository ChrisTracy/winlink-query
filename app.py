import os
import logging
from modules import db
from modules import smtp
from modules import logger
import threading
import time

# Interval Configuration
interval = int(os.getenv('INTERVAL', '60'))

#Function to repeat email fetch on interval
def run_interval(interval):
    while True:
        smtp.fetch_emails()
        time.sleep(interval)

# Setup the databse if it does not exist
db.setup_database()

# Set up a thread to run the function
thread = threading.Thread(target=run_interval, args=(interval,))
thread.start()