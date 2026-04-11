# Implementation Plan (Version-2)

This file is maintained by the agent during the current task.

The plan describes how the task in CURRENT_TASK.md (Version-2) will be completed.

Keep it concise and actionable.

---

## Task Summary

Implement Version-2 of WeatherApp: extend the existing GUI so the MainWindow displays current weather (unchanged layout/styling) and a 48-hour hourly forecast table below the current fields. Changes are limited to the files named in CURRENT_TASK.md and must respect the project constraints.

---

## Files To Modify

- `src/weatherapp/gui/main_window.py` (add UI for 48-hr hourly forecast table, SVG icon rendering in forecasts at 24×24, layout insertion beneath existing current-weather widgets)
- `src/weatherapp/gui/worker.py` (include hourly forecast payload in emitted weather_fetched signal — structured next-48-hours list or DataFrame-like serializable structure)
- `src/weatherapp/app.py` (no functional changes expected; only run-time entry may be used to smoke-test the window)

Do not modify other modules. Follow CONSTRAINTS.md: keep diffs minimal and avoid refactoring unrelated code.

---

## Implementation Steps

1. Update this PLAN.md (done).

2. Worker changes (src/weatherapp/gui/worker.py):
   - Extend the dict emitted by weather_fetched to include an "hourly" key whose value is a list of 48 items (one per hour). Each item will be a plain dictionary with these keys in this order: Time, svg, description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip, Wind, Gusts, Visibility, UV.
   - Populate each hourly dict using the same indices and conversions already used by the format/show_weather.py module (temperature rounding, visibility meters→miles, precipitation aggregation rain+showers, etc.).
   - Keep lazy imports and background-threading behavior. Do not change signal names or threading model. Emit the same weather_fetched signal (payload extended) and keep fetch_failed unchanged.

3. MainWindow changes (src/weatherapp/gui/main_window.py):
   - Add a QLabel/QWidget area below the current fields with the header "48-hr forecast:".
   - Implement a scrollable (if necessary) grid or simple QGridLayout presenting 13 columns with headers in this order: Time, Description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip, Wind, Gusts, Visibility, UV.
   - For the Description column, render the SVG icon at 24×24 to the left of the textual description (parenthetical description text remains acceptable). Use QSvgRenderer → QPixmap → QLabel.setPixmap to render icons; fallback to clearing the QLabel on error.
   - Display 48 rows (one per hour); if vertical space is constrained, allow the area to be scrollable (QScrollArea) while preserving the current-weather layout and styling unchanged.
   - Ensure updates to forecast widgets only happen in the GUI/main thread (in on_weather_fetched) and are defensive against missing fields.
   - Preserve current-weather widgets exactly (no changes to their layout or styling), except for adding the forecast block beneath them.

4. Testing & validation:
   - Run an import check: PYTHONPATH=src python -c "import weatherapp" to ensure no import-time errors (PyQt6 availability considered).
   - If PyQt6 is not present in the environment, document the limitation in `agent_control/STATE.md` and skip runtime GUI checks.
   - If available, launch the app manually (python -m weatherapp.app) to visually verify the forecast table and icon rendering.

5. Documentation & state updates:
   - Update `agent_control/STATE.md` describing what was changed (files modified, limitations, how the hourly payload is structured).
   - Run the self-checklist in `agent_control/CHECKLIST.md` and correct any issues.

---

## Data contract (worker → GUI)

The `weather_fetched` signal will continue to emit a single dict. Add key:

- "hourly": list[dict]
  - Each dict fields (string keys):
    - "Time": string (e.g. "10:00 AM")
    - "svg": string (svg filename, relative to src/weatherapp/icons)
    - "description": string (short human description, e.g. "overcast")
    - "Temp": numeric (raw value; MainWindow will format/display as desired)
    - "Feels": numeric
    - "Humidity": numeric (percent)
    - "Cloud cover": numeric (percent)
    - "Rainfall": numeric (inches)
    - "Snowfall": numeric (inches)
    - "Precip.": numeric (percent)
    - "Wind": numeric (mph)
    - "Gusts": numeric (mph)
    - "Visibility": numeric (miles)
    - "UV": numeric

Rationale: keep the payload simple and serializable; let MainWindow handle display formatting where reasonable.

---

## Risks and Unknowns

- PyQt6 might not be available in the execution environment; runtime GUI verification may be impossible. Record this in STATE.md if encountered.
- Exact font metrics differ across platforms; target is functional alignment and readability, not pixel-perfect layout.
- Large changes to main_window.py must avoid touching existing current-weather layout; ensure tests/import-check pass before runtime testing.

---

## Verification

- Modules import successfully (PYTHONPATH=src).
- Application launches (if environment supports PyQt6).
- Current weather UI is unchanged visually and functionally.
- 48-hour forecast appears below current fields with 13 columns and correct headers.
- Forecast description icons render at ~24×24 and update on new data.
- Refresh button and automatic 10-minute refresh continue to trigger data fetch and UI updates.

---

Next step: implement worker payload changes and MainWindow forecast UI. Proceed when instructed or confirm to continue now.