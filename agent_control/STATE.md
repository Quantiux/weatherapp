# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 5.0

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
