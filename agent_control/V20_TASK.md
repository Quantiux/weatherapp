# Current Task

Implement Version-2 of WeatherApp.

Goal
Extend the Version-1.3 GUI so the window visibly displays both current weather fields and hourly weather forecast for next 48 hours.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

Worker requirements:

- Version 1.3 worker already fetches all weather data including hourly and daily forecasts, but emits only current weather fields.

- Version-2 worker must also emit hourly weather forecast data for the next 48 hours.

MainWindow UI requirements:

- Current weather fields as in Version-1.3 **without any modification to their layout or styling**.

- Next 48-hour Hourly weather forecast below current weather fields, under the header "48-hr forecast:".

- SVG images for description field of hourly forecasts must be rendered in 24×24 pixel size each.

- Forecast data fields should be displayed in 13-column grid layout, with colum headers in this order: Time, Description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip, Wind, Gusts, Visibility, UV.

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
Visibility: 65mi
UV Index: 0

48-hour forecast:
48-hour forecast:
Time Description Temp Feels Humidity Cloud cover Rainfall Snowfall Precip. Wind Gusts Visibility UV
10:00 AM wi-cloudy.svg (overcast) 48°F 44°F 65% 100% 0.0in 0.0in 68% 2mph 2mph 55mi 0.40
11:00 AM wi-day-sprinkle.svg (moderate drizzle) 45°F 41°F 75% 100% 0.0in 0.0in 67% 4mph 6mph 32mi 0.30
12:00 PM wi-cloudy.svg (overcast) 47°F 43°F 76% 100% 0.0in 0.0in 27% 4mph 8mph 31mi 0.25
1:00 PM wi-cloudy.svg (overcast) 49°F 44°F 75% 100% 0.0in 0.0in 10% 7mph 16mph 31mi 0.80

Implementation requirements:

- Add a QLabel dedicated to displaying the icon.
- Load the SVG file referenced by the "svg" field from the worker payload.

Example path resolution:

`src/weatherapp/icons/<svg_filename>`

Use Qt classes to render SVG:

Preferred approach:

- QSvgRenderer
- QPixmap
- QLabel.setPixmap()

Simpler acceptable approach:

- QPixmap if Qt can load the SVG directly.

Icon display requirements in forecast:

The icon must:

• appear before the weather description (description in parentheses)
• scale to approximately 24×24 pixels
• update whenever new weather data arrives

Behavior:

Inside MainWindow.on_weather_fetched():

1. read svg filename from payload
2. construct icon file path
3. load SVG
4. render into QPixmap
5. set QLabel pixmap

Refresh behavior

Icon must update whenever weather data refreshes.

Success criteria

- Application launches successfully
- Current weather and next 48-hr forecasts are displayed
- Refresh button triggers data fetch
- Data and display auto-refresh every 10 minutes.
