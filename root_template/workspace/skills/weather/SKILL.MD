---
name: weather
description: Use this skill to get current weather and forecasts. Uses HTTP requests to fetch data from weather APIs. Handles geocoding (city name to coordinates) and data parsing. Weather Skill.
---

# 1. Command Syntax
The `do_http_request` tool accepts arguments. Use this tool to interact with weather services.

`method`: ALWAYS use GET for weather requests.json_body: ALWAYS set to null (or None) for GET requests.url: Construct the URL based on the Open-Meteo API structure.

# 2. Workflow & Logic
To get weather for a city, you cannot just pass the city name to the weather API directly. You must follow this two-step workflow:

## Step 1: Geocoding (City to Coordinates)
You need the latitude and longitude for the weather API. Use the Open-Meteo Geocoding API.

**URL Construction**: https://geocoding-api.open-meteo.com/v1/search?name={CITY_NAME}&count=1&language=en&format=json
**Action**: Call `do_http_request` with the URL above. Parse the response JSON. Find the first result (results[0]).Extract latitude and longitude.

## Step 2: Fetch Weather Data
Now use the coordinates to get the actual weather.

**URL Construction**: Base URL: https://api.open-meteo.com/v1/forecast

**Required Parameters:**

- `latitude`: from Step 1
- `longitude`: from Step 1
- `current_weather`: true (to get current temperature and wind)
- `hourly`: temperature_2m, relative_humidity_2m, weather_code (optional, for detailed forecast)

**Example URL**: https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current_weather=true

**Action**: Call `do_http_request`. Parse the `current_weather` object from the response.

# 3. Data Presentation Strategy
When the user asks for weather, follow these synthesis rules:

## A. Standard Output
Always present the data clearly:
- Temperature: Report in Celsius (default) or Fahrenheit if requested.
- Wind: Report speed (km/h) and direction.
- Condition: Decode the weathercode (WMO code).

Keep in mind that that all timestamps from API are in UTC time. Convert the UTC time in local timezone

## B. Interpreting Weather Codes
The API returns a numeric weathercode. Translate it to human text:
- 0: Clear sky ☀️
- 1, 2, 3: Mainly clear, partly cloudy, overcast ⛅
- 45, 48: Fog 🌫️
- 61, 63, 65: Rain 🌧️
- 71, 73, 75: Snow ❄️
- 95, 99: Thunderstorm ⛈️

## C. Error Handling
- If the city is not found in Step 1, tell the user "City not found" and ask for clarification.
- If the HTTP request fails, report the error status code.

# Example User Interaction:
User: "What is the weather in Tokyo?"

1. Agent calls `do_http_request` for geocoding "Tokyo". Gets lat=35.68, lon=139.69.
2. Agent calls `do_http_request` for weather using those coords.
3. Agent replies: "The current weather in Tokyo is Clear sky with a temperature of 22°C and wind speed of 15 km/h."