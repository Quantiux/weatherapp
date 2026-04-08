# Current Task

Implement Version-1 of WeatherApp.

Goal:
Improve minimal Version-05 PyQt6 GUI to display all fetched current weather data.

Requirements

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify module `src/weatherapp/gui/main_window.py` as needed to emit all current weather data fetched by `src/weatherapp/gui/worker.py` (no need to change this module). Make appropriate changes to the docstrings and comments to maintain readability.

MainWindow

- QWidget window
- Display current weather data and emoji icon
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

Version-1 constraints

- No hourly or daily forecast views
- No styling
- No networking changes

Success criteria

- Application launches successfully
- Current weather is displayed
- Refresh button triggers data fetch
