# Current Task

Implement Version-0 of WeatherApp.

Goal:
Create a minimal PyQt6 GUI displaying current weather conditions.

Requirements

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Create these modules:

`src/weatherapp/gui/main_window.py`  
`src/weatherapp/gui/worker.py`
`src/weatherapp/gui/__init__.py`  
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

Version-0 constraints

- No hourly or daily forecast views
- Minimal layout
- No styling
- No networking changes

Success criteria

- Application launches successfully
- Current weather is displayed
- Refresh button triggers data fetch
