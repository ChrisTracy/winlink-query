# APRS Query Service

I developed this project for APRS Amateur Radio enthusiasts, leveraging OpenAI's capabilities to process user input. It allows users to send an email requesting weather data for any location worldwide. The system utilizes Open Weather Map to retrieve accurate weather information and automatically responds with an email containing the detailed weather data.

## Using My Environment

I am committed to personally hosting and supporting this system, provided it is used responsibly. Currently, this service is exclusively available to users affiliated with winlink.org. If you have an active amateur radio call sign and a winlink email, you can test the service by sending an email in the following formats:

**To:** aprsquery@gmail.com

### Current Weather
To get the current weather for a specific location:
- **Subject:** weather:current
- **Body:** Houston, Texas

### 7-Day Forecast
To request a 7-day weather forecast for a specific zip code:
- **Subject:** weather:daily
- **Body:** Provide the weather for zip code 90048

### Hourly Forecast
To obtain an hourly weather forecast using coordinates and the metric system:
- **Subject:** weather:hourly
- **Body:** Provide the weather forecast for 51.510047731805415, -0.04960678749831505. Provide the results in metric.

Feel free to phrase your email requests in your own style, as this system utilizes OpenAI for processing input. However, for the best results, keep your requests concise.



## Setup your own server

1. Create a docker-compose.yml file:
```bash
nano docker-compose.yml
```

2. Add this to the YAML file with your own parameters. You will need a Gmail account, an Open AI API key and an Open Weather Map API ley:
```yml
version: '3.8'

services:
  app:
    image: christracy/aprs-query
    restart: always
    environment:
      #SMTP Variables
      SMTP_USERNAME: <example@gmail.com>        # Email address used for processing
      SMTP_PASSWORD: <your secure password>             # Email password (app password)
      ALLOWED_DOMAINS: "winlink.org, example.com"  # Domains that are allowed to use the service. Use "*" to allow all domains
      
      #Open AI Variables
      OAI_API_KEY: <your open ai api key> #API key for Open AI

      #Open Weather Variables
      WEATHER_API_KEY: <your open weather map api key> # API key for Open Weather Map

      ### Optional parameters ###
      #IMAP_HOST: imap.gmail.com      # Change this to use something outside of gmail (not tested)
      #SMTP_HOST: smtp.gmail.com      # Change this to use something outside of gmail (not tested)
      #INTERVAL: 60                   # How often (seconds) to check the accounts inbox for new messages
      #RATE_LIMIT: 30                 # The number of seconds before a single account can email the service again. Violation = discard request without response
      #OAI_MODEL: gpt-3.5-turbo-0125  # GPT model to use for formating location to coordinates and units
      #OAI_MAX_TOKENS: 50             # Max tokens used to process the GPT request
      #LOG_LEVEL: INFO                # Log level for the server (INFO/DEBUG)
```

9. Bring up your stack by running:

```bash
docker compose up -d
```