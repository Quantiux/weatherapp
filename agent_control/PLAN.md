# Implementation Plan

This file is maintained by the agent during the current task.

The plan describes how the task in CURRENT_TASK.md will be completed.

Keep it concise and actionable.

---

## Task Summary

Implement Version-1 of WeatherApp: extend the PyQt6 GUI so the MainWindow visibly displays all current weather fields emitted by the Worker and updates them in on_weather_fetched(). Maintain existing threading, manual refresh, and automatic refresh behavior.

---

## Files To Modify

- `src/weatherapp/gui/main_window.py` (add QLabel widgets for each required field and update them in on_weather_fetched)
- `src/weatherapp/gui/worker.py` (no change required if it already emits the richer dict)
- `src/weatherapp/app.py` (no changes expected)

---

## Implementation Steps

1. Update `agent_control/PLAN.md` (this file) to reflect Version-1 work and files to modify.
2. Modify `src/weatherapp/gui/main_window.py`:
   - Add QLabel widgets for the following fields in order: Weather (icon + description), Temperature (shows apparent temperature too), Humidity, Cloud cover, Rainfall total, Snowfall, Precipitation probability, Wind (speed and gusts), Visibility, UV index.
   - Use a simple QVBoxLayout and keep UI updates inside on_weather_fetched().
   - Keep existing thread/worker connections and refresh behavior unchanged.
3. Run a quick import check (PYTHONPATH=src) to ensure modules import without raising errors at import time.
4. If import succeeds, update `agent_control/STATE.md` describing the implemented changes and modified files.
5. Run the self-checklist in `agent_control/CHECKLIST.md` and fix any issues found.

---

## Risks or Unknowns

- Exact units for some fields (rainfall, snowfall, temperature) depend on the data layer; UI will display raw numeric values with reasonable unit labels (°F for temperature, "in" for precipitation, "mi" for visibility) mirroring existing examples.
- If PyQt6 is not available in the execution environment, import checks may fail; report this in the final summary.

---

## Verification

- Application modules import without errors when PYTHONPATH=src.
- MainWindow updates all new QLabel widgets inside on_weather_fetched() using data emitted by Worker.
- GUI thread remains non-blocking and worker thread connections remain unchanged.
