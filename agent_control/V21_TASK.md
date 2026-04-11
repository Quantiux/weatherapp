# Current Task

Implement Version-2.1 of WeatherApp.

Goal
Improve visual display styling of the main window without changing data fetching, threading, or application structure.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`

MainWindow UI requirements:

- Visibility field of current and forecast data should display the following value w/o quotes:
  - "Clear" if visibility is 10 miles or more
  - "Fair" if visibility is 5 miles or more but less than 10 miles
  - "Poor" if visibility is 1 mile or more but less than 5 miles
  - "Zero" otherwise

- UV Index field of current and forecast data should display the following value w/o quotes:
  - "Low" if UV Index is 2 or less
  - "Moderate" if UV Index is 3 to 5
  - "High" if UV Index is 6 to 7
  - "Very High" if UV Index is 8 to 10
  - "Extreme" if UV Index is 11 or more

- Description column of Hourly forecast should display SVG icon and descrtipion (in parentheses as already set) **without any space**.

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

48-hour forecast:
Time Description Temp Feels Humidity Cloud cover Rainfall Snowfall Precip. Wind Gusts Visibility UV
10:00 AM wi-cloudy.svg(overcast) 48°F 44°F 65% 100% 0.0in 0.0in 68% 2mph 2mph Clear Low
11:00 AM wi-day-sprinkle.svg(moderate drizzle) 45°F 41°F 75% 100% 0.0in 0.0in 67% 4mph 6mph Clear Low
12:00 PM wi-cloudy.svg(overcast) 47°F 43°F 76% 100% 0.0in 0.0in 27% 4mph 8mph Clear Low
1:00 PM wi-cloudy.svg(overcast) 49°F 44°F 75% 100% 0.0in 0.0in 10% 7mph 16mph Clear Low

Success criteria

- Application launches successfully
- Current weather and next 48-hr forecasts are displayed
- Refresh button triggers data fetch
- Data and display auto-refresh every 10 minutes.
