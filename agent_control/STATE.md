# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 5.1

Description:

Version-5.1 adds a compact, user-editable location selector to the MainWindow
(above the tab bar) and wires it to the existing background Worker. Users may
enter latitude and longitude and press Apply to validate the inputs, update the
MainWindow's coords, call Worker.set_coords(lat, lon), and trigger an immediate
fetch via the existing request_fetch signal. Periodic refresh continues to use
self.coords automatically.

---

## Implemented Changes

- MainWindow: `src/weatherapp/gui/main_window.py`
  - Added a compact Location row with `self.lat_input`, `self.lon_input`, and
    `self.apply_location_button` placed above the tabs so the UI layout remains
    stable.
  - Inputs use `QDoubleValidator` for basic numeric entry and are initialized
    from `DEFAULT_COORDS` so startup behavior is unchanged.
  - Implemented `_apply_new_location()` which validates ranges (-90..90,
    -180..180), updates `self.coords`, calls `self._worker.set_coords(lat, lon)`
    defensively, and emits `self.request_fetch.emit()` to trigger an immediate
    refresh.

- agent_control/PLAN.md: Updated to Version-5.1 plan and steps.

---

## Files Modified

- `src/weatherapp/gui/main_window.py` (add location row, validator, apply handler)
- `agent_control/PLAN.md` (updated plan to reflect Version-5.1)
- `agent_control/STATE.md` (this file)

---

## Validation Performed

- Import check: `PYTHONPATH=src python -c "import weatherapp"` succeeded in
  this environment (no import-time errors introduced).
- Constructed Worker and MainWindow objects (without starting the Qt event
  loop) to verify attributes exist: `Worker().coords` and `MainWindow().coords`
  reflect defaults and the new widgets are present.

---

## Known Limitations

- `_apply_new_location()` uses `QMessageBox.warning` for invalid input which is
  a blocking dialog. This is acceptable for this small feature but could be
  changed to a non-blocking in-UI status message in a future iteration.
- Live GUI verification requires PyQt6 and a display server; run `PYTHONPATH=src
  python -m weatherapp.app` locally to fully verify the interaction.

---

## Next Steps

1. Run the app locally and verify:
   - Inputs show default coords
   - Entering valid coords and pressing Apply triggers a fetch using the new
     coords
   - Entering invalid coords shows a warning and does not trigger a fetch
2. If desired, replace blocking QMessageBox warnings with a non-blocking
   status label in the top row for a smoother UX.


Description:

Version-5.0 removes hard-coded coordinates inside the Worker and enables the GUI to provide dynamic latitude/longitude at runtime. The Worker stores coordinates as an instance attribute and exposes a pyqtSlot to accept updates from the GUI. MainWindow now holds its own coords and passes them to the Worker before each fetch. No changes were made to signal names, the worker threading model, or the emitted weather data structures.

---

## Implemented Changes

- Worker: `src/weatherapp/gui/worker.py`
  - Added `self.coords` instance attribute (tuple(lat, lon)), initialized to the previous default development coordinates.
  - Added `@pyqtSlot(float, float) def set_coords(self, lat, lon)` to accept coordinate updates from the GUI. Inputs are defensively validated.
  - `fetch()` now calls `fetch_weather(self.coords)` (previous behavior preserved when GUI doesn't set coords).

- MainWindow: `src/weatherapp/gui/main_window.py`
  - Added `self.coords` (initialized to the same default) so future UI controls can change location.
  - Ensure the Worker is constructed with the initial coords at startup.
  - Before each fetch (manual refresh and periodic timer), call `worker.set_coords(self.coords[0], self.coords[1])` so the Worker always uses the latest coordinates.

- App startup: `src/weatherapp/app.py`
  - No functional changes required; MainWindow still constructs and starts the worker thread.

---

## Files Modified

- `src/weatherapp/gui/worker.py` (added self.coords and set_coords slot; fetch uses self.coords)
- `src/weatherapp/gui/main_window.py` (store self.coords; pass coords to worker before fetch)
- `agent_control/STATE.md` (updated to Version-5.0)

---

## Validation Performed

- Import check performed in this environment: `PYTHONPATH=src python -c "import weatherapp"` — no import-time errors after the changes.
- Constructs MainWindow and Worker objects (without starting the Qt event loop) to verify new slot and attribute exist. Manual GUI runtime testing is recommended locally with PyQt6 and a display server.

---

## Known Limitations

- PyQt6 and a display server are required for live GUI verification. This environment may not support a full GUI launch; manual verification is recommended locally with PyQt6 installed.
- Visual rendering may vary across platforms and font configurations; minor alignment tweaks may be necessary after manual inspection.

---

## Next Steps

1. Run the app locally with PyQt6 installed: `PYTHONPATH=src python -m weatherapp.app` and verify:
   - App launches normally and the first fetch occurs using the default coordinates.
   - Clicking "Refresh Now" triggers a fetch that uses the current `self.coords` value.
2. If desired, add a small unit/smoke test that constructs Worker and MainWindow (without the Qt event loop) and verifies `set_coords` updates the worker's coords attribute.
