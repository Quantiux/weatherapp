# Implementation Plan (Version-5.3)

Goal:

Add geocoding so the Location input accepts either "lat,lon" (unchanged) or a
free-form location query (city name, city+state, ZIP/PIN code). Geocoding must run
in the Worker thread, must not block the GUI, and must preserve all Version-5.2
behavior when numeric coordinates are provided.

Files to modify (exact):

- src/weatherapp/gui/worker.py  (add set_location_query slot, _geocode_location helper,
  call fetch() after successful geocode, emit fetch_failed on error)
- src/weatherapp/gui/main_window.py  (replace lat/lon inputs with a single
  QLineEdit self.location_input, add request_geocode signal, update Apply handler
  to detect numeric lat/lon vs free-form and emit request_geocode)
- src/weatherapp/app.py  (no changes expected; mention here only to confirm
  app entry remains compatible)
- agent_control/STATE.md (update after implementation)

Architecture / Approach (constraints):

- Keep changes minimal and localized to Worker and MainWindow.
- Worker.fetch() signature remains unchanged and still accepts only coords.
- Geocoding must be performed in the Worker thread; MainWindow only emits a
  request_geocode(str) signal.
- No new long-running synchronous calls in the GUI thread.
- Do not add new dependencies unless strictly needed (use Open-Meteo Geocoding
  which is a simple HTTP GET; use the stdlib urllib.request or requests only if
  justified — prefer urllib to avoid adding dependencies).

Acceptance criteria:

- Entering numeric "lat,lon" continues to work exactly as before.
- Entering "Ann Arbor", "Ann Arbor, MI", or a ZIP/PIN triggers geocoding in the
  Worker and results in the same UI update flow as existing lat/lon fetches.
- On geocode failure the Worker emits fetch_failed("Location not found") and GUI
  shows a QMessageBox without crashing or clearing existing weather.
- No blocking calls in GUI thread; threading and signals preserved.

Step-by-step Tasks (bite-sized):

Task 1 — Inspection (done)

Objective: Locate exact insertion points and symbol names in the two source
files so edits are minimal and deterministic.

Deliverable: list of exact symbols to change (see implementation notes below).

Task 2 — Worker: add geocoding slot and helper

Objective: Inside src/weatherapp/gui/worker.py add:

- New pyqtSlot:

    @pyqtSlot(str)
    def set_location_query(self, query: str) -> None:
        # Called from GUI thread (queued). Performs _geocode_location and on
        # success updates self.coords and calls self.fetch(). On failure emits
        # fetch_failed("Location not found") or other descriptive message.

- New helper method:

    def _geocode_location(self, query: str) -> tuple[float, float]:
        # Query Open-Meteo Geocoding API and return (lat, lon) for the first
        # reasonable match. Raise an exception on network errors or no results.

Implementation notes for Worker:
- Use urllib.request or urllib.parse (stdlib) to avoid adding requests.
- Respect timeout and raise exception on non-200 or parse errors.
- Update self.coords only after successful geocode and before calling
  self.fetch() so the normal fetch flow runs unchanged.
- Ensure fetch() remains a no-argument pyqtSlot() and is reused.

Task 3 — MainWindow: replace inputs, add signal, update Apply handler

Objective: Replace the two QLineEdit fields (self.lat_input, self.lon_input) with
one QLineEdit named self.location_input and add a new signal:

    request_geocode = pyqtSignal(str)

Modify the Apply button handler to:
1. Read and strip self.location_input.text(). If empty show QMessageBox warning.
2. If text matches float,float pattern (two comma-separated numbers) parse
   as lat and lon and run the existing numeric path: validate ranges, call
   worker.set_coords(lat, lon), update self.coords and emit request_fetch() as
   before.
3. Otherwise: emit self.request_geocode.emit(query) and return (do not perform
   network calls in GUI). Keep the UI responsive.

Wire request_geocode to self._worker.set_location_query when the worker is
available (same style as existing connections). The slot call will be queued to
the worker thread.

Task 4 — Worker flow after geocode

- set_location_query performs geocode (blocking inside worker thread only),
  updates self.coords, then calls self.fetch() (queued slot call within same
  thread is fine; since it's invoked from the worker thread directly it's a
  normal method call). If geocode raises or returns no result, emit
  fetch_failed("Location not found").

Task 5 — Error handling and validation

- Empty input: GUI warns before emitting anything.
- Invalid numeric formats: GUI falls back to treating as query; let Worker
  handle errors and emit fetch_failed.
- Worker must catch network errors and emit fetch_failed with a friendly
  message.

Task 6 — Smoke & import checks

- Run: PYTHONPATH=src python -c "import weatherapp" (no new import-time heavy
  dependencies)
- Construct Worker and MainWindow objects locally (requires PyQt6 in environment)
  and verify attributes exist.

Task 7 — Update agent_control/STATE.md

- Record Version: 5.3, files modified, verification performed, known limitations
  or required Python versions.

Task 8 — Self-review & checklist

- Run through agent_control/CHECKLIST.md and verify all items pass.

Estimated effort: 45–120 minutes depending on network code debugging.

Next action (what I'll do now if you confirm):

- Implement Worker.set_location_query and _geocode_location in
  src/weatherapp/gui/worker.py (Task 2).
- Modify src/weatherapp/gui/main_window.py: replace inputs with
  self.location_input, add request_geocode signal, and update Apply handler to
  detect numeric vs query input (Task 3).

If you'd like me to proceed, confirm and I'll apply the code changes and run
the smoke/import checks described above.