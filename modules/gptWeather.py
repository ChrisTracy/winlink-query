import requests
import json
from .logger import logger
from modules import openWeatherHelper

def generate_weather_report(location_content, oai_api_key, weather_api_key, type, oai_model='gpt-3.5-turbo-0125', oai_max_tokens=50):

    # Headers for the HTTP request
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {oai_api_key}'
    }

    # Data payload for the Open AI request
    data = {
        'model': f'{oai_model}',
        'messages': [
            {"role": "system", "content": "You are an expert at parsing data and finding coordinates based on input. I am going to provide you some text containing coordinates or a location. Your job is to respond in json format with the coordinates. You may need to lookup the coordinates if a location (city,zip code, etc) is provided. You also need to determine unit type. The options are imperial and metric (watch for things like farenheit, celcius). Default to imperial if nothing is provided.The output should ALWAYS have these parameters: lat:latitude, long:longitude, units:units"},
            {"role": "user", "content": f"{location_content}"}
        ],
        'max_tokens': oai_max_tokens,
        "temperature": 0.5,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    
    # Endpoint URL for Open AI ChatCompletion
    oai_url = 'https://api.openai.com/v1/chat/completions'

    # Make the POST request to Open AI
    oai_response1 = requests.post(oai_url, headers=headers, data=json.dumps(data))

    # Check if the request was successful
    if oai_response1.status_code == 200:
        response_data = oai_response1.json()
        try:
            location_data = json.loads(response_data['choices'][0]['message']['content'].strip())
            print(location_data)

            latitude   = location_data['lat']
            longitude  = location_data['long']
            units      = location_data['units']
        except KeyError as e:
            logger.error(f"KeyError - {str(e)}: Necessary location data not found in the response.")
            return None  # Exit the function if critical data is missing

        # Open Weather URLs for smaller json
        class weatherURL:
            daily = f"https://api.openweathermap.org/data/3.0/onecall?units=imperial&exclude=current,minutely,hourly&lat={latitude}&lon={longitude}&appid={weather_api_key}"
            current = f"https://api.openweathermap.org/data/3.0/onecall?units=imperial&exclude=daily,minutely,hourly&lat={latitude}&lon={longitude}&appid={weather_api_key}"
            hourly = f"https://api.openweathermap.org/data/3.0/onecall?units=imperial&exclude=daily,minutely,current&lat={latitude}&lon={longitude}&appid={weather_api_key}"

        # Construct the URL for weather
        weather_url = getattr(weatherURL, type)

        #Request the weather
        wmap_response1 = requests.get(weather_url)

        # Function to validate that all necessary parameters are provided
        def validate_params(latitude, longitude, units):
            if latitude is None or longitude is None or units is None:
                return False
            return True

        # Check if the weather request was successful
        if wmap_response1.status_code == 200:    
            wmap_json_response = wmap_response1.json()
            
            # Validate latitude, longitude, and units before processing
            if validate_params(latitude, longitude, units):
                if type == "daily":
                    forecast_report = openWeatherHelper.generate_daily_forecast(wmap_json_response, lat=latitude, long=longitude, unit=units)
                    return forecast_report
                if type == "current":
                    forecast_report = openWeatherHelper.generate_current_forecast(wmap_json_response, lat=latitude, long=longitude, unit=units)
                    return forecast_report
                if type == "hourly":
                    forecast_report = openWeatherHelper.generate_hourly_forecast(wmap_json_response, lat=latitude, long=longitude, unit=units)
                    return forecast_report
            else:
                print("Error: Missing required parameters (latitude, longitude, or units).")
        else:
            print(f"Failed to retrieve data: {wmap_response1.status_code}")


    else:
        logger.error(f"Failed to retrieve data from OpenAI: {oai_response1.status_code}")
        return None  # Exit the function if the API call was unsuccessful