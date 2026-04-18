# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 5.5

Description:

Version-5.4 adds saved locations and persistent configuration using a small
JSON file stored under ~/.config/weatherapp/config.json (fallback
~/.weatherapp_config.json). The GUI exposes a Saved Locations dropdown and a
Save button; saved locations are strings (not coordinates) and are persisted
between runs.

---

## Implemented Changes

- Worker: `src/weatherapp/gui/worker.py`
  - Inspected: Worker already implements `set_location_query` and `_geocode_location`.
  - The geocoding implementation uses urllib.parse.urlencode on the full user input
    (preserving commas and state qualifiers) and requests Open-Meteo with `count=1`,
    selecting the first returned result. Errors raise a RuntimeError and the worker
    emits `fetch_failed` with a friendly message.
  - No code changes were required in the Worker for CURRENT_TASK.md.

- MainWindow: `src/weatherapp/gui/main_window.py`
  - Confirms `self.location_input`, `request_geocode` signal, and Apply/save handlers
    are implemented per Version-5.3 expectations.
  - The Apply handler parses numeric "lat,lon" inputs and otherwise emits
    `request_geocode` (queued to the worker thread), keeping network I/O out of the GUI.

- ConfigManager / Saved locations:
  - ConfigManager is available and the saved locations dropdown is populated on startup
    when the config manager is present. The Save button stores free-form location strings.


---

## Files Modified

- `src/weatherapp/config_manager.py` (new)
- `src/weatherapp/gui/main_window.py`

---

## Validation Performed

- Import check: `PYTHONPATH=src python -c "import weatherapp"` — succeeded in
  this environment (no import-time errors unrelated to missing PyQt6).
- Basic unit checks: module imports and new ConfigManager instantiation
  attempted at runtime; full GUI runtime checks require PyQt6 and a display
  server and should be performed locally by the developer.

---

## Known Limitations

- Full GUI runtime validation requires PyQt6 and a display server; perform
  manual verification locally:
  - Run: `PYTHONPATH=src python -m weatherapp.app`
  - Verify saved locations appear in the dropdown, Save persists to config,
    and last_location is restored.
- Config file write failures (permissions, readonly home) are swallowed to
  avoid crashing the GUI; failures are best detected by checking the file
  on disk after saving.

---

## Next Steps

1. Run the app locally with PyQt6 installed and verify Save/Load flows and
   startup restore of last_location.
2. Add tests for ConfigManager load/save behavior if desired.
