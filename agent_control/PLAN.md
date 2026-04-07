# Implementation Plan

This file is maintained by the agent during the current task.

The plan describes how the task in CURRENT_TASK.md will be completed.

Keep it concise and actionable.

---

## Task Summary

Implement Version-0 of WeatherApp: create a minimal PyQt6 GUI that displays current weather (temperature, description, emoji/icon), supports manual and automatic refresh, and uses a background worker (QThread) to call existing data functions.

---

## Files To Create

- `src/weatherapp/gui/__init__.py`
- `src/weatherapp/gui/worker.py`
- `src/weatherapp/gui/main_window.py`
- `src/weatherapp/app.py`

---

## Files To Modify

None.

---

## Implementation Steps

1. Create `src/weatherapp/gui/__init__.py` to define the gui package.
2. Implement `Worker` in `src/weatherapp/gui/worker.py` using QThread pattern:
   - Worker runs in a QThread and exposes a `fetch()` slot.
   - Worker calls `weatherapp.data.get_weather_data.fetch_weather()` and `weatherapp.format.show_weather` helpers as needed.
   - Worker emits `weather_fetched(dict)` on success and `fetch_failed(str)` on error.
3. Implement `MainWindow` in `src/weatherapp/gui/main_window.py`:
   - Minimal QWidget showing temperature, description (with icon text), and a "Refresh Now" QPushButton.
   - Connect button to call the Worker's `fetch()` via a queued signal.
   - Start a QTimer that triggers a refresh every 10 minutes (600000 ms).
   - Show error messages using QMessageBox when fetch fails.
   - Ensure GUI updates occur only from the main thread (use signals/slots).
4. Implement `src/weatherapp/app.py` as the application entry point to create QApplication, instantiate MainWindow, and start the GUI.
5. Run a quick import smoke test to ensure modules import correctly (no runtime network calls at import time).
6. Update `agent_control/STATE.md` with files added and a short summary.
7. Run the checklist in `agent_control/CHECKLIST.md` and fix any issues.

---

## Risks or Unknowns

- Exact return structure of fetch_weather() (the worker will treat its return as opaque and only extract needed current fields; tests will mock network calls).
- get_weather_icon() is referenced in CURRENT_TASK.md but not present as a standalone function; the worker will rely on weather_code_mapper helpers via show_weather.format helpers or will request only the description provided by format.show_weather's parsing functions.

---

## Verification

- Application imports without errors.
- MainWindow can be created without performing network requests.
- Worker emits `weather_fetched` when fetch is called (to be validated by running the app with network mocked or with a dry-run environment).

---


