# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 5.3

Description:

Version-5.3 adds geocoding so the Location input accepts free-form queries
("city", "city, state", ZIP/PIN) as well as the existing "lat,lon" format.
Geocoding runs in the Worker thread using the Open-Meteo geocoding API and
preserves the threading and fetch flow from previous versions.

Version-5.2 made the NOW tab clock reflect the selected location's local time
by including the timezone in the worker payload and having MainWindow store and
use a ZoneInfo instance when formatting the NOW tab time label.

---

## Implemented Changes

- Worker: `src/weatherapp/gui/worker.py`
  - Added result["timezone"] inclusion when the API provides a timezone string.

- MainWindow: `src/weatherapp/gui/main_window.py`
  - Added `self._active_timezone` to store the current location timezone.
  - on_weather_fetched now updates `self._active_timezone` from the payload
    defensively using ZoneInfo.
  - _update_time_label now uses the active timezone when present and falls
    back to system time otherwise.

---

## Files Modified

- `src/weatherapp/gui/worker.py`
- `src/weatherapp/gui/main_window.py`
- `agent_control/PLAN.md` (updated earlier to describe Version-5.2)
- `agent_control/STATE.md` (this file)

---

## Validation Performed

- Import check: `PYTHONPATH=src python -c "import weatherapp"` — succeeded in
  this environment (no import-time errors unrelated to missing PyQt6).
- Constructed Worker and MainWindow objects would require PyQt6; in this
  headless environment PyQt6 is not installed so full construction was not
  executed here. Local smoke tests should be run with PyQt6 available.

---

## Known Limitations

- ZoneInfo requires Python 3.9+. If running on older Python versions, the
  behavior falls back to system time; document this in release notes if needed.
- Full GUI runtime validation requires PyQt6 and a display server; perform
  manual verification locally:
  - Run: `PYTHONPATH=src python -m weatherapp.app`
  - Verify that changing coordinates and fetching updates the NOW tab clock.

---

## Next Steps

1. Run the app locally with PyQt6 installed and verify the NOW tab time updates
   to the location's timezone on app launch, after coordinate changes, after
   refresh, and on timer ticks.
2. If desired, add unit/smoke tests that call on_weather_fetched with a sample
   payload containing `{"timezone": "Asia/Tokyo"}` and verify the label text
   includes JST-equivalent time.
