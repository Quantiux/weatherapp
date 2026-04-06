# WeatherApp

**WeatherApp** is a lightweight desktop weather application built with **PyQt6**. It retrieves weather data from the Open-Meteo API and presents current conditions, a short-term hourly forecast, and a multi-day outlook in a clean graphical interface.

The application is designed to be fast, simple, and easy to run on a local machine.

---

## Features

* Current weather conditions
* **48-hour hourly forecast**
* **10-day forecast**
* Clean PyQt6 desktop interface
* Lightweight and responsive
* Simple architecture designed for reliability

At present the application uses a **fixed location**. A city search feature may be added in a future version.

---

## Requirements

* Python 3.12 or newer
* Poetry (for dependency management)

---

## Installation

Clone the repository:

```bash
mkdir WeatherApp
cd WeatherApp
git clone https://github.com/Quantiux/weatherapp.git
```

Install dependencies using Poetry:

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

* City search and location selection
* Settings panel (units, refresh interval)
* Weather icons and visual improvements
* Caching of forecast data
* Packaging as a standalone desktop application

---

## License

MIT License

