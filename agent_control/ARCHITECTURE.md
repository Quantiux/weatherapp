# Architecture

Project root:
`~/Projects/WeatherApp/`

Runtime code:
`src/weatherapp/`

Tests:
`tests/`

Existing modules:

`src/weatherapp/data/get_weather_data.py`  
Fetches weather data from the API.

`src/weatherapp/format/show_weather.py`  
Formats weather information for display.

`src/weatherapp/utils/weather_code_mapper.py`  
Maps weather condition codes to descriptions/icons.

GUI modules (to be created):

`src/weatherapp/gui/main_window.py`  
Main PyQt6 window.

`src/weatherapp/gui/worker.py`  
Background worker thread for fetching weather data.

`src/weatherapp/app.py`  
Application entry point.

Architectural rules:

- Use PyQt6 for GUI components.
- All network calls must run in background workers.
- The GUI thread must never perform blocking operations.
- Do not modify existing modules unless explicitly instructed.
- Do not reorganize project directories unless instructed.
