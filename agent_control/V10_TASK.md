# Current Task

Implement Version-1 of WeatherApp.

Goal
Extend the Version-0.5 GUI so the window visibly displays all current weather fields emitted by Worker.

Requirements

Constraint priority rule
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

MainWindow UI requirements

The window must contain QLabel widgets that display in this order:

Weather description with emoji icon
Temperature (Apparent temperature)
Relative humidity
Cloud cover
Rainfall total
Snowfall
Precipitation probability
Wind speed (wind gusts)
Visibility
UV index

These values must be updated inside `MainWindow.on_weather_fetched()`.

Layout

A simple QVBoxLayout is sufficient.
Each field may be displayed on its own QLabel.

Example display format:

Weather: wi-day-cloudy.svg (partly cloudy)
Temperature: 72°F (Feels like: 70°F)
Humidity: 40%
Cloud cover: 25%
Rainfall: 0.1 in
Snowfall: 0 in
Precip: 10%
Wind: 6 mph (Gusts: 10 mph)
Visibility: 9.5 mi
UV index: 3

Threading

Use QThread + Worker pattern.
Worker.fetch() runs in the worker thread.
MainWindow updates UI only via signals.

Refresh behavior

Manual refresh button calls Worker.fetch via signal.
Automatic refresh every 10 minutes using QTimer.

Version-1 constraints

No forecasts
No styling
No networking changes

Success criteria

- Application launches successfully
- Current weather is displayed as listed above
- Refresh button triggers data fetch
