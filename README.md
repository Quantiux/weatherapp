# WeatherApp

**WeatherApp** is a lightweight desktop weather application built with **PyQt6**. It retrieves weather data from the Open-Meteo API and presents current conditions, 24-hour hourly forecast, and 7-day outlook in a clean interface.

The application is designed to be fast, simple, and easy to run on a local machine.

---

## Features

- Current weather conditions
- **24-hour hourly forecast**
- **7-day forecast**
- Clean PyQt6 desktop interface
- Lightweight and responsive
- Simple architecture designed for reliability

---

## Requirements

- Python 3.12 or newer
- Poetry (for dependency management)

---

## Installation

1. Prerequisites:

For linux platforms, starting with Qt 6.5, the `xcb` platform plugin - which allows Qt to communicate with the X11 window system - has explicit dependency on libxcb-cursor library, which is often not included in minimal or standard desktop installs. Make sure the `libxcb-cursor0` package is installed on your system. If not, install with:

```bash
sudo apt update
sudo apt install libxcb-cursor0
```

2. Clone the repository:

```bash
mkdir WeatherApp
cd WeatherApp
git clone https://github.com/Quantiux/weatherapp.git
```

3. Install dependencies using Poetry:

```bash
poetry install
```

---

## Running the Application

Run the application with:

```bash
poetry run python -m weatherapp.main
```

This starts the PyQt6 desktop interface and retrieves the latest weather data.

---

## Data Source

Weather data is provided by the **Open-Meteo API**, which supplies free weather forecasts without requiring an API key.

---

## Future Improvements

Planned or possible enhancements:

---

## License

MIT License
