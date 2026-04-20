# Version 5.14 - README.md Rewrite

## Task Overview

Rewrite and improve the project's `README.md` to make it suitable for a public GitHub repository.

The current README is outdated and minimal. The goal is to produce a **clear, polished, professional README** that accurately describes the current state of the application.

Do **not modify any source code**. Only update `README.md`.

---

## Project Summary

WeatherApp is a lightweight **desktop weather application written in Python using PyQt6**.

It retrieves weather data from the **Open-Meteo API** and displays:

- Current conditions
- A **24-hour hourly forecast**
- A **7-day forecast**

The application emphasizes:

- fast startup
- minimal dependencies
- simple architecture
- a clean desktop UI

---

## Required README Sections

The new README should contain:

1. Project title
2. Short project description
3. Feature overview
4. Screenshots section
5. Installation instructions
6. Running the application
7. Data source
8. Project structure (optional but encouraged)
9. Future improvements
10. License# Recommended Implementationion

---

## Screenshots

Add a Screenshots section showing the UI.

Use the provided images:

- `docs/screenshots/current.png`
- `docs/screenshots/hourly.png`
- `docs/screenshots/daily.png`

Show them using standard Markdown image syntax.

Suggested layout:

```
## Screenshots

### Current Conditions

![Current weather](docs/screenshots/current.png)

### 24-Hour Forecast

![Hourly forecast](docs/screenshots/hourly.png)

### 7-Day Forecast

![7-day forecast](docs/screenshots/daily.png)
```

---

## Installation Instructions

Preserve the Linux dependency note for Qt:

`libxcb-cursor0` must be installed for Qt6 on many Linux systems.

Example installation command for Debian/Ubuntu/Mint system:

```
sudo apt update
sudo apt install libxcb-cursor0
```

Python package dependencies are managed with **Poetry**.

Installation flow should be:

```
git clone https://github.com/Quantiux/weatherapp.git
cd weatherapp
poetry install
```

---

## Running the Application

The application should be started with:

```
poetry run python -m weatherapp.app
```

---

## Data Source

Mention that weather data is provided by **Open-Meteo** and does not require an API key.

---

## Style Requirements

The README should:

- Be concise but professional
- Use clean Markdown formatting
- Avoid unnecessary marketing language
- Avoid emojis
- Avoid claims about features not present in the codebase
- Accurately reflect the application

---

## Expected Output

Modify only:

```
README.md
```

Do **not modify any Python files**.

The final README should be **ready for a public GitHub repository**.

## Notes

The application is designed to run locally and does not require a server or API key.

Focus on clarity, simplicity, and accuracy.
