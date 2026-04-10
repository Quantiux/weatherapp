# Current Task

Implement Version-2.2 of WeatherApp.

Goal:
Improve Version-2.1 GUI so the hourly forecasts displays next 24-hr forecasts beginning with the hour after current hour. Furthermore, round all wind and gusts values to nearest integer.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

Worker requirements:

- Version 2.1 worker already emits current weather data and 48-hr hourly forecasts.

- Version-2.2 worker must emit current weather (as before) and hourly forecasts for the **next 24 hours beginning with the hour after current hour**.

MainWindow UI requirements:

- Current weather fields as in Version 2.1 without any modification to their layout or styling.

- Next 24-hour Hourly weather forecast below current weather fields, under the header "24-hour forecast:".

- Wind and Gusts values in current and forecast data fields should be rounded to the nearest integer.

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

Success criteria

- Application launches successfully
- Current weather and next 24-hr forecasts are displayed
- Refresh button triggers data fetch and all display fields update accordingly
- All data and display fields auto-refresh every 10 minutes.
