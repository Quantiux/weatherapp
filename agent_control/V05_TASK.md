# Current Task

Implement Version-0.5 of WeatherApp.

Goal:
Improve minimal Version-0 PyQt6 GUI to display richer current weather conditions, to include all fetched current weather data.

Requirements

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

MainWindow

- QWidget window
- Display temperature, description, and emoji icon
- Include "Refresh Now" button
- Show error messages if fetch fails

Threading

- Use QThread + Worker pattern
- Worker has fetch() slot
- Worker emits weather_fetched(dict)

Refresh behavior

- Automatic refresh every 10 minutes via QTimer
- Manual refresh via button

Worker behavior

- Call get_weather_data()
- Call get_weather_icon()
- Package results into dict and emit signal

Version-0.5 constraints

- No hourly or daily forecast views
- Minimal layout
- No styling
- No networking changes

Success criteria

- Application launches successfully
- Current weather is displayed
- Refresh button triggers data fetch
