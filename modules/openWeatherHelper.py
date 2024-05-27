from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

# Function to convert temperatures between Celsius and Fahrenheit
def convert_temperature(temp, unit):
    if unit == 'metric':
        return (temp - 32) * 5.0/9.0
    else:
        return temp

# Function to convert wind speed from mph to kph
def convert_wind_speed(speed, unit):
    if unit == 'metric':
        return speed * 1.60934
    else:
        return speed

# Function to find the timezone based on latitude and longitude
def get_timezone(lat, long):
    tf = TimezoneFinder()
    try:
        # Convert lat and long to float if they are not already
        lat = float(lat)
        long = float(long)
    except ValueError:
        raise ValueError("Latitude and Longitude must be convertible to float")
        
    timezone_str = tf.timezone_at(lat=lat, lng=long)  # Get timezone string from coordinates
    if timezone_str is None:
        raise ValueError("Invalid coordinates for timezone determination")
    return pytz.timezone(timezone_str)

# Function to convert UTC timestamp to local date using latitude and longitude
def get_date(timestamp, lat, long):
    timezone = get_timezone(lat, long)
    utc_time = datetime.utcfromtimestamp(timestamp)
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    return local_time.strftime('%A, %B %d, %Y')

# Function to convert UTC timestamp to local date and time using latitude and longitude
def get_date_time(timestamp, lat, long):
    timezone = get_timezone(lat, long)
    utc_time = datetime.utcfromtimestamp(timestamp)
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(timezone)
    return local_time.strftime('%A, %B %d, %Y at %H:%M')

# Function to parse daily forcast output from Open Weather
def generate_daily_forecast(data, lat, long, unit='imperial'):
    email_forecast = f"Weather Forecast for {lat}, {long}:\n\n"
    for day in data["daily"]:
        date = get_date(day["dt"], lat=lat, long=long)
        summary = day["summary"]
        temp_day = convert_temperature(day["temp"]["day"], unit)
        temp_min = convert_temperature(day["temp"]["min"], unit)
        temp_max = convert_temperature(day["temp"]["max"], unit)
        wind_speed = convert_wind_speed(day["wind_speed"], unit)
        description = day["weather"][0]["description"]

        email_forecast += f"Date: {date}\n"
        email_forecast += f"Summary: {summary}\n"
        email_forecast += f"Day Temperature: {temp_day:.1f}°{'C' if unit == 'metric' else 'F'}\n"
        email_forecast += f"Min Temperature: {temp_min:.1f}°{'C' if unit == 'metric' else 'F'}\n"
        email_forecast += f"Max Temperature: {temp_max:.1f}°{'C' if unit == 'metric' else 'F'}\n"
        email_forecast += f"Weather: {description}\n"
        email_forecast += f"Wind Speed: {wind_speed:.1f} {'km/h' if unit == 'metric' else 'mph'}\n"
        email_forecast += "---\n\n"
    
    # Adding alerts to the forecast
    if "alerts" in data:
        email_forecast += "Alerts:\n\n"
        for alert in data["alerts"]:
            start_date = get_date(alert["start"], lat=lat, long=long)
            end_date = get_date(alert["end"], lat=lat, long=long)
            email_forecast += f"Event: {alert['event']}\n"
            email_forecast += f"From: {start_date} to {end_date}\n"
            email_forecast += f"Details: {alert['description']}\n"
            email_forecast += "---\n\n"

    return email_forecast

# Function to parse current forcast output from Open Weather
def generate_current_forecast(data, lat, long, unit='imperial'):
    # Gather basic current weather details
    current_weather = data["current"]
    date = get_date(current_weather["dt"], lat=lat, long=long)
    temp = convert_temperature(current_weather["temp"], unit)
    feels_like = convert_temperature(current_weather["feels_like"], unit)
    wind_speed = convert_wind_speed(current_weather["wind_speed"], unit)
    description = current_weather["weather"][0]["description"]

    # Format the forecast in a readable email-style
    email_forecast = (
        f"Current Weather Forecast for {lat}, {long} on {date}:\n\n"
        f"Temperature: {temp:.1f}°{'C' if unit == 'metric' else 'F'}\n"
        f"Feels Like: {feels_like:.1f}°{'C' if unit == 'metric' else 'F'}\n"
        f"Weather: {description}\n"
        f"Wind Speed: {wind_speed:.1f} {'km/h' if unit == 'metric' else 'mph'}\n"
        "---\n\n"
    )

    # Adding alerts to the forecast if they exist
    if "alerts" in data:
        email_forecast += "Alerts:\n\n"
        for alert in data["alerts"]:
            start_date = get_date(alert["start"], lat=lat, long=long)
            end_date = get_date(alert["end"], lat=lat, long=long)
            email_forecast += f"Event: {alert['event']}\n"
            email_forecast += f"From: {start_date} to {end_date}\n"
            email_forecast += f"Details: {alert['description']}\n"
            email_forecast += "---\n\n"

    return email_forecast

# Function to parse hourly forcast output from Open Weather
def generate_hourly_forecast(data, lat, long, unit='imperial'):
    email_forecast = f"Hourly Weather Forecast for {lat}, {long}:\n\n"
    
    for hour in data["hourly"]:
        date_time = get_date_time(hour["dt"], lat=lat, long=long)
        temp = convert_temperature(hour["temp"], unit)
        feels_like = convert_temperature(hour["feels_like"], unit)
        wind_speed = convert_wind_speed(hour["wind_speed"], unit)
        description = hour["weather"][0]["description"]

        email_forecast += (
            f"Date & Time: {date_time}\n"
            f"Temperature: {temp:.1f}°{'C' if unit == 'metric' else 'F'}\n"
            f"Feels Like: {feels_like:.1f}°{'C' if unit == 'metric' else 'F'}\n"
            f"Weather: {description}\n"
            f"Wind Speed: {wind_speed:.1f} {'km/h' if unit == 'metric' else 'mph'}\n"
            "---\n\n"
        )

    if "alerts" in data:
        email_forecast += "Alerts:\n\n"
        for alert in data["alerts"]:
            start_date = get_date_time(alert["start"], lat=lat, long=long)
            end_date = get_date_time(alert["end"], lat=lat, long=long)
            email_forecast += f"Event: {alert['event']}\n"
            email_forecast += f"From: {start_date} to {end_date}\n"
            email_forecast += f"Details: {alert['description']}\n"
            email_forecast += "---\n\n"

    return email_forecast