# APRS Query Service

## Overview
The APRS Query Service is designed for APRS Amateur Radio enthusiasts, integrating OpenAI's advanced capabilities to accurately process user inputs. This service allows users to send emails to request weather data for any global location, utilizing Open Weather Map for precise weather updates. The response includes comprehensive weather information delivered directly via email.

## Access and Usage
This system is personally hosted and maintained with a commitment to responsible use. Access is currently restricted to users affiliated with winlink.org. Eligible users must have an active amateur radio call sign and a winlink.org email address.

### How to Use
Email your weather requests to `weather@radiolake.com` with the following formats:

#### Current Weather *(using city, state in the body)*
- **Subject:** `weather:current`
- **Body:** `Houston, Texas`

#### 7-Day Forecast *(using a zip code in the body)*
- **Subject:** `weather:daily`
- **Body:** `90048`

#### Hourly Forecast *(using coordinates with unit preference)*
- **Subject:** `weather:hourly`
- **Body:** `provide the weather for 51.510047731805415, -0.04960678749831505 using the metric system`

The system leverages OpenAI to understand various phrasing styles, though it's recommended to keep requests straightforward for optimal processing. Results are returned in imperial format by default but you can request metric by simply asking in your email (eg, `London, Egland in metric format`).

## Setting Up Your Server
To deploy your own instance of the APRS Query Service, follow these steps:

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

3. Bring up your stack by running:

```bash
docker compose up -d
```

## Support

If you find the service helpful or enjoy using it, please consider supporting me.

[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/ctracy)
