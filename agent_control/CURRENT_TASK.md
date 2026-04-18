# Current Task: Version 5.6 — Desktop Dashboard & Hero Section

## 🎯 Objective

Transform the interface into a desktop-optimized dashboard by implementing a prominent "Current Weather" hero section and a background auto-refresh mechanism.

## 🧱 Architectural Principles

- **Desktop Ergonomics:** Use horizontal space effectively. The Hero section should span the width of the window above the tabs.
- **Resource Management:** Load SVGs from `src/weatherapp/icons/` using the logic in `weather_code_mapper.py`.
- **Thread Safety:** The background refresh timer must trigger existing worker signals to avoid UI freezes.

## 🛠 Requirements

### 1. Backend Data Expansion (`src/weatherapp/data/get_weather_data.py`)

- Modify the `params` dictionary to request the `current` data block from Open-Meteo:
  `["temperature_2m", "relative_humidity_2m", "is_day", "weather_code", "wind_speed_10m"]`.
- Ensure `fetch_weather` passes this block through to the return payload.

### 2. SVG Integration (`src/weatherapp/gui/main_window.py`)

- **Hero Widget:** Create a `QWidget` placed at the very top of the `QVBoxLayout`.
- **Layout:** Use a `QHBoxLayout` for the Hero Widget:
  - **Left:** A `QSvgWidget` (or `QLabel` with `QSvgRenderer`) to display the condition icon. Size should be fixed (e.g., 100x100 or 128x128).
  - **Right:** A `QVBoxLayout` containing:
    - Current Temperature (Large, bold font, e.g., 42pt).
    - Condition Description (Medium font, e.g., "Partly Cloudy").
    - Location Name (Small font, showing the current city).

### 3. Background Refresh & Status

- **QTimer:** Implement a 15-minute background timer (`900,000 ms`) that triggers `self.request_fetch.emit()`.
- **Status Bar:** Add a `QStatusBar` to the main window.
  - Display "Last Updated: [Time]" upon every successful data fetch.

### 4. Icon Mapping Logic

- Integrate `src/weatherapp/utils/weather_code_mapper.py` into the `on_weather_fetched` flow.
- Ensure `is_day` (0 or 1) from the API is used to select the correct day/night SVG variant.

## 🧪 Success Criteria

1. The app launches and shows a large weather icon and the current temperature above the tabs.
2. The UI remains responsive while the icon renders.
3. The Status Bar accurately reflects the age of the data.
4. Resizing the window keeps the Hero section properly aligned on the left/top.

## 🚫 Non-Goals for v5.6

- Do not implement charts/graphs yet.
- Do not add system tray integration yet.
