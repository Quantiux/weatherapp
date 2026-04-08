# Implementation Plan

This file is maintained by the agent during the current task.

The plan describes how the task in CURRENT_TASK.md will be completed.

Keep it concise and actionable.

---

## Task Summary

Implement Version-0.5 of WeatherApp: enhance the minimal PyQt6 GUI to display a richer set of current weather fields (temperature, description/icon, humidity, wind, visibility, UV, precipitation), support manual and automatic refresh, and use a background worker (QThread) to call existing data functions.

---

## Files To Create

- `src/weatherapp/gui/__init__.py` (already present)

## Files To Modify

- `src/weatherapp/gui/worker.py` (expanded to emit richer current weather dict)
- `src/weatherapp/gui/main_window.py` (already displays basic fields; will be used as-is)
- `src/weatherapp/app.py` (already present; no changes required)

---

## Implementation Steps

1. Update `src/weatherapp/gui/worker.py` to extract the full set of current fields used by format.show_weather and emit them in `weather_fetched` as a plain dict. Keep imports lazy and handle structured-access failures by emitting the raw response as fallback.
2. Ensure `main_window.py` safely consumes the richer dict, updating temperature and description as before. The window will continue to show temperature and a compact description; additional fields are included in the payload for future UI enhancements.
3. Run quick import checks to verify no imports trigger network calls at import time.
4. Update `agent_control/STATE.md` summarizing changes and files modified.
5. Run the checklist in `agent_control/CHECKLIST.md` and fix any issues.

---

## Risks or Unknowns

- Exact response object interface from fetch_weather; handled via try/except and fallback to raw response.
- UI layout remains minimal; future tasks will add more visualizations.

---

## Verification

- Application modules import without errors.
- Worker emits `weather_fetched` with richer dict when `fetch()` is invoked.
- GUI updates remain confined to the main thread and no blocking occurs on startup.
