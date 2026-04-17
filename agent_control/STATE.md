# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 5.4

Description:

Version-5.4 adds saved locations and persistent configuration using a small
JSON file stored under ~/.config/weatherapp/config.json (fallback
~/.weatherapp_config.json). The GUI exposes a Saved Locations dropdown and a
Save button; saved locations are strings (not coordinates) and are persisted
between runs.

---

## Implemented Changes

- Worker: `src/weatherapp/gui/worker.py`
  - (No behavioral changes) Worker remains stateless regarding config and
    continues to accept only coordinates. Geocoding remains implemented as in
    Version-5.3.

- MainWindow: `src/weatherapp/gui/main_window.py`
  - Added `self._active_timezone` to store the current location timezone.
  - on_weather_fetched now updates `self._active_timezone` from the payload
    defensively using ZoneInfo.
  - _update_time_label now uses the active timezone when present and falls
    back to system time otherwise.
  - Added a QComboBox `self.saved_locations` and a QPushButton `self.save_location_button`.
  - ConfigManager is instantiated when available and the dropdown is populated
    on startup. Selecting a saved location fills the input and triggers a
    geocode/fetch. The Save button stores the current input string (avoids
    duplicates) and refreshes the dropdown.

- New module: `src/weatherapp/config_manager.py`
  - Implements ConfigManager with load/save/add_location/remove_location/set_last_location
    and safe file handling (backup on corruption).

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
