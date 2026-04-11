# Current Task

Implement Version-3 of WeatherApp.

Goal
Extend the Version-2.2 GUI so the window visibly displays current weather, 24-hr hourly forecast and next 7-day forecast.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

Consult these modules as needed for reference, but **do not modify them**:

`src/weatherapp/data/get_weather_data.py`
`src/weatherapp/format/show_weather.py`
`src/weatherapp/utils/weather_code_mapper.py`

Worker requirements:

- Version 2.2 worker already fetches all weather data, but emits only current weather and hourly forecast fields.

- Version-3 worker must also emit daily weather forecast data for the next 7 days, **beginning with tomorrow**.

- Daily forecast should contain two additional data fields: daily sunrise and sunset times.

MainWindow UI requirements:

- Current weather and hourly forecast fields as in Version-2.2 **without any modification to their layout or styling**.

- Next 7-day daily weather forecast below hourly forecats fields, under the header "7-day forecast:".

- Weekday names in date field of daily forecasts must be displayed in parentheses after the date without any space in between.

- Sunrise and sunset times in daily forecasts must be displayed in 12-hour format with AM/PM, without seconds, and with no space between time and AM/PM (e.g., "7:01AM", "8:10PM").

- SVG images for description field of daily forecasts must be rendered in 24×24 pixel size each, with parentheted description text on its right without any space (same as in hourly forecast).

- Daily forecast data fields should be displayed in 15-column grid layout, with colum headers in this order: Date, Description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip., Wind, Gusts, Visibility, UV, Sunrise, Sunset.

Example layout:

wi-cloudy.svg (overcast)
Temperature: 45°F
Feels like: 38°F
Rain Prob.: 50%
Rainfall: 0.0in
Snowfall: 0.0in
Humidity: 70%
Cloud cover: 100%
Wind: 8 mph
Gusts: 11 mph
Visibility: Clear
UV Index: Low

24-hour forecast:
Time Description Temp Feels Humidity Cloud cover Rainfall Snowfall Precip. Wind Gusts Visibility UV
10:00 AM wi-cloudy.svg(overcast) 48°F 44°F 65% 100% 0.0in 0.0in 68% 2mph 2mph Clear Low
11:00 AM wi-day-sprinkle.svg(moderate drizzle) 45°F 41°F 75% 100% 0.0in 0.0in 67% 4mph 6mph Clear Low
12:00 PM wi-cloudy.svg(overcast) 47°F 43°F 76% 100% 0.0in 0.0in 27% 4mph 8mph Clear Low
1:00 PM wi-cloudy.svg(overcast) 49°F 44°F 75% 100% 0.0in 0.0in 10% 7mph 16mph Clear Low

7-day forecast:
Date Description Temp Feels Humidity Cloud cover Rainfall Snowfall Precip. Wind Gusts Visibility UV Sunrise Sunset
04-10(Fri) wi-day-sprinkle.svg(moderate drizzle) 47°F 43°F 83% 96% 0.0in 0.0in 13% clear 5mph 10mph High 7:01AM 8:10PM
04-11(Sat) wi-cloudy.svg(overcast) 45°F 40°F 70% 60% 0.0in 0.0in 0% Clear 5mph 9mph High 6:59AM 8:11PM
04-12(Sun) wi-day-sprinkle.svg(heavy drizzle) 53°F 46°F 72% 97% 0.0in 0.0in 17% Clear 13mph 27mph High 6:58AM 8:12PM
04-13(Mon) wi-day-showers.svg(slight rain showers) 65°F 61°F 82% 100% 0.0in 0.0in 29% Clear 16mph 31mph High 6:56AM 8:13PM

Success criteria

- Application launches successfully
- Current weather, next 24-hr forecasts, and next 7-day forecasts are displayed
- Refresh button triggers data fetch and refreshes all displayed data fields, including icons
- All data and display fields auto-refresh every 10 minutes.
