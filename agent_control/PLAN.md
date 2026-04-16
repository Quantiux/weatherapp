# Implementation Plan (Version-5.1)

Goal:

Add a small user-editable location selector to the MainWindow and wire it to the
existing background Worker so users can enter latitude and longitude and fetch
weather for arbitrary coordinates. Preserve existing behavior and threading; keep
changes minimal and localized to the MainWindow.

Scope & constraints:

- Modify only these files:
  - src/weatherapp/gui/main_window.py
  - agent_control/PLAN.md (this file)
  - agent_control/STATE.md (documentation update after implementation)
- Do NOT modify worker.py, data-parsing, networking, or threading model.
- Do NOT add new dependencies.
- Follow CONSTRAINTS.md and AGENT.md rules (PEP8 ≤100 chars, defensive error
  handling, no blocking GUI thread).

Assumptions / current context:

- Worker already exposes @pyqtSlot(float, float) set_coords(lat, lon) and
  MainWindow already stores self.coords and uses it when passing coords before
  requesting a fetch. Periodic and manual refresh wrappers call set_coords prior
  to emitting request_fetch. DEFAULT_COORDS is defined in worker.py.

Approach (high level):

1. Inspect MainWindow to find the natural place to add a compact location row
   above the tabs/top controls.
2. Add QLineEdit inputs for latitude and longitude with QDoubleValidator to
   reduce invalid input. Add an Apply QPushButton.
3. Implement _apply_new_location() to read, validate ranges, update
   self.coords, call worker.set_coords(lat, lon) defensively, then emit
   request_fetch to trigger an immediate refresh.
4. Wire the Apply button and, optionally, Enter key handling. Ensure periodic
   refresh uses the updated self.coords automatically.
5. Run import and construction smoke checks (without launching full GUI).
6. Update agent_control/STATE.md and run the checklist.

Step-by-step plan:

Task 1 — Inspect code (read-only)
- Open src/weatherapp/gui/main_window.py and confirm:
  - where top control area is created (above tabs)
  - that self.coords exists and DEFAULT_COORDS is imported
  - how refresh wrapper passes coords to the worker

Deliverable: exact insertion point and variable names to use for widgets.

Task 2 — Add widgets and layout
- In MainWindow.__init__:
  - Import QLineEdit and QDoubleValidator.
  - Create: self.lat_input = QLineEdit(), self.lon_input = QLineEdit(),
    self.apply_location_button = QPushButton("Apply").
  - Attach a QDoubleValidator(-180.0, 180.0, 6, self) to both fields; clamp
    latitude programmatically to -90..90 on Apply.
  - Place widgets in a compact QHBoxLayout placed above the tab widget (minimal
    disturbance to existing layout).
  - Initialize inputs with DEFAULT_COORDS formatted (e.g. {:.6f}).

Task 3 — Implement apply handler
- Add method _apply_new_location(self) with responsibilities:
  - Read texts, strip, convert to float, show QMessageBox.warning on parse
    failure or out-of-range values.
  - Validate ranges: -90 <= lat <= 90, -180 <= lon <= 180.
  - Update self.coords = (lat, lon).
  - Try calling self._worker.set_coords(lat, lon) inside try/except. If that
    raises, defensively set self._worker.coords = (lat, lon).
  - Emit self.request_fetch.emit() to trigger immediate fetch.
- Connect self.apply_location_button.clicked.connect(self._apply_new_location).

Task 4 — Keep periodic/manual refresh behavior
- No changes expected: existing _on_refresh_with_coords wrapper calls
  self._worker.set_coords(self.coords...) before emitting request_fetch; ensure
  self.coords is updated by Apply so periodic refresh uses latest coords.

Task 5 — Smoke & import checks
- Run:
  - PYTHONPATH=src python -c "import weatherapp"
  - PYTHONPATH=src python - <<'PY'\nfrom weatherapp.gui.worker import Worker\nfrom weatherapp.gui.main_window import MainWindow\nw = Worker()\n# construct MainWindow without starting event loop\nmw = MainWindow()\nprint(mw.coords)\nPY
- Expect no import errors and mw.coords reflects DEFAULT_COORDS; calling
  mw._apply_new_location logic can be tested via direct method call in a
  dev-shell.

Task 6 — Update STATE.md
- Document: Version: 5.1, brief description, files modified, verification steps,
  and known limitations (e.g., QMessageBox is blocking; prefer non-blocking
  status messages in future versions).

Task 7 — Self-review & checklist
- Run through agent_control/CHECKLIST.md manual items. Fix style, remove unused
  imports, ensure only the MainWindow was changed, and no blocking I/O occurs
  on the GUI thread.

Files to change (exact):
- src/weatherapp/gui/main_window.py
- agent_control/PLAN.md
- agent_control/STATE.md (update after implementation)

Tests / validation
- Import check: PYTHONPATH=src python -c "import weatherapp"
- Construct Worker and MainWindow without running the QT event loop to verify
  attributes exist and Apply handler does not crash when invoked with valid
  numeric strings.
- Manual GUI test recommended locally: verify inputs show defaults, Apply
  updates worker coords and triggers a fetch, invalid inputs show warnings and
  do not trigger fetch.

Risks, tradeoffs, and open questions
- Risk: Layout space is tight on small windows; keep the location row compact
  and consider hiding on narrow widths in a future task (out of scope).
- Risk: QMessageBox is blocking; current plan uses it for simplicity. If blocking
  UX is unacceptable, switch to a non-blocking status label in a follow-up.
- Tradeoff: Validator + programmatic range check gives good UX without
  overcomplication.

Estimated effort: 20–45 minutes for coding and smoke checks.

Next action: Edit src/weatherapp/gui/main_window.py to add the Location row and
_apply_new_location handler. After the change, run the import/construction
smoke checks and update agent_control/STATE.md.


Goal:

Enable dynamic coordinates for Worker so the GUI can provide latitude/longitude at runtime. Remove hard-coded coordinates inside Worker.fetch() and ensure the GUI may update the Worker before each fetch. No visible UI changes in this version.

Scope & constraints:

- Modify only these files as required:
  - src/weatherapp/gui/worker.py
  - src/weatherapp/gui/main_window.py
  - src/weatherapp/app.py
- Keep changes minimal and localized to the coordinates handling and the refresh flow.
- Do NOT change signal names, returned weather data structures, or forecasting/parsing logic.
- Do NOT change the Worker threading model.
- Do NOT add new modules or third-party dependencies.
- Preserve default coordinates so the app launches normally if the GUI hasn't provided coords yet.
- Follow CONSTRAINTS.md and AGENT.md coding standards (PEP8, ≤100 chars line length, defensive error handling).

Assumptions / current context:

- The Worker currently uses hard-coded coordinates inside fetch(); the data client and fetch_weather(self.coords) call exist and must keep same signature.
- The GUI has an existing refresh workflow that triggers worker.fetch(). We will keep that flow but pass coordinates beforehand.
- The worker emits the same signals and payloads; only internal coordinate source will change.

Approach (high level):

1. Inspect current code to find exact locations and variable names for Worker, fetch(), refresh button handler in MainWindow, and application startup flow in app.py.
2. Modify Worker to hold coords as an instance attribute with sensible defaults, expose a pyqtSlot set_coords(lat, lon) to update self.coords, and ensure fetch() uses self.coords when calling fetch_weather(self.coords).
3. Modify MainWindow to hold its own self.coords default, update the refresh button click handler to call worker.set_coords(*self.coords) before invoking worker.fetch(). Also ensure any automatic periodic refresh calls follow same pattern.
4. Modify app.py initialization so default coordinates are defined and passed to MainWindow and to the Worker before the first fetch (or ensure MainWindow passes them at startup). Keep startup flow unchanged otherwise.
5. Run import checks and (where possible) a local smoke-run to validate the app launches and refresh works. Document changes in agent_control/STATE.md and run agent_control/CHECKLIST.md before finishing.

Step-by-step plan:

Task 1 — Inspect the code (read-only)
- Open and inspect:
  - src/weatherapp/gui/worker.py — locate Worker class, fetch() implementation, any existing coords variable usage, and current imports.
  - src/weatherapp/gui/main_window.py — locate MainWindow.__init__, refresh button handler(s), where worker.fetch() is called, and where the worker object is created/assigned.
  - src/weatherapp/app.py — find app startup sequence and how MainWindow / Worker are instantiated and wired.
- Record existing signal/slot wiring and any helper methods used for fetch() calls.

Deliverable: list of exact function/class/variable names to change and the default coordinates currently used (if present).

Task 2 — Update Worker: instance coords + set_coords slot
- In src/weatherapp/gui/worker.py:
  - Add an instance attribute `self.coords` to Worker.__init__ (prefer tuple (lat, lon)). Initialize with the current default coordinates used in the repo so behavior is unchanged if GUI doesn't set coords.
  - Add a pyqtSlot(float, float) named set_coords(self, lat, lon) that updates `self.coords` atomically. Include defensive checks (validate numeric types, clamp to plausible ranges or log and ignore invalid input).
  - Modify fetch() so it no longer references any module-level hard-coded coordinates; instead call `fetch_weather(self.coords)` (or the existing client call that previously used the hard-coded values). Keep the rest of fetch() logic untouched.
  - Keep lazy imports inside fetch() if present to avoid import-time heavy dependencies.
  - Add or update docstrings to explain the new attribute and slot.

Task 3 — Update MainWindow: store coords and pass to worker on refresh
- In src/weatherapp/gui/main_window.py:
  - Add `self.coords` to MainWindow.__init__ with the same default coordinates used by the Worker. This avoids startup differences.
  - Locate the refresh button handler (e.g., on_refresh_clicked or similar). Right before the code that calls `worker.fetch()` (or emits the refresh signal), call `self.worker.set_coords(self.coords[0], self.coords[1])` so the worker receives updated coords; then proceed to the existing fetch call.
  - Ensure any automatic periodic refresh paths also call worker.set_coords(...) prior to fetch.
  - If the MainWindow constructs the Worker and passes initial values, ensure it passes the default coords to the Worker before the first fetch. If the Worker is created elsewhere, ensure the initial handshake happens before the first scheduled fetch.
  - Do not change signal names, do not alter how the worker is moved to its thread, and do not block the GUI thread.

Task 4 — App initialization: default coords and first fetch
- In src/weatherapp/app.py:
  - Ensure default coords are defined (e.g., DEFAULT_COORDS = (lat, lon)) and passed to MainWindow or used to initialize the Worker before the first fetch.
  - If MainWindow currently sets its own default coords, ensure app.py doesn't need changes; otherwise, add a single-line initialization or pass through constructor args so behavior is deterministic.

Task 5 — Import & smoke checks (non-destructive)
- Run: `PYTHONPATH=src python -c "import weatherapp"` to check for import-time errors.
- If PyQt6 and a display are available locally, run: `PYTHONPATH=src python -m weatherapp.app` and verify manually:
  - App launches normally (no crashes).
  - The first fetch occurs and shows weather as before.
  - Clicking Refresh still triggers worker.set_coords(...) + worker.fetch() and updates data as before.
- If GUI can't be launched in this environment, at minimum assert that imports and object construction (MainWindow, Worker) succeed without starting the GUI event loop.

Task 6 — Update agent_control/STATE.md
- After implementation, update `agent_control/STATE.md`:
  - Version: 5.0
  - Brief description of changes made.
  - Files modified and why.
  - Any limitation or outstanding items.

Task 7 — Self-review & checklist
- Run through agent_control/CHECKLIST.md manually and fix issues: PEP8 (≤100 chars), docstrings, only required files changed, no blocking calls on GUI thread.
- Do NOT commit or stage changes (CONSTRAINTS.md).

Files likely to change (exact):
- src/weatherapp/gui/worker.py
- src/weatherapp/gui/main_window.py
- src/weatherapp/app.py
- agent_control/STATE.md (documentation only)

Tests / validation
- Import check: `PYTHONPATH=src python -c "import weatherapp"`
- Unit-ish: construct Worker and MainWindow objects without starting Qt loop to ensure constructors and new slot exist. Example (in dev env):
  - `PYTHONPATH=src python - <<'PY'
from weatherapp.gui.worker import Worker
from weatherapp.gui.main_window import MainWindow
w = Worker()
# call set_coords and ensure attribute updates
w.set_coords(12.34, 56.78)
print(w.coords)
PY`
- Manual GUI validation: run app and test refresh flow.

Risks, tradeoffs, and open questions
- Risk: Widget or wiring names differ from assumed ones. Mitigation: Task 1 inspects exact names; implement minimal changes and prefer calling worker.set_coords rather than changing constructor wiring.
- Risk: Multiple code paths call worker.fetch() (scheduled timers, startup, manual refresh). Mitigation: Identify all call sites and ensure set_coords is called before fetch() at each path.
- Tradeoff: Keeping defaults in both Worker and MainWindow duplicates a tiny bit of data but keeps startup robust. Alternative is to source defaults centrally (app.py) — choose minimal edits: set default in app.py and pass to both places if easy.
- Open question: Where is the Worker instance created relative to MainWindow? If created inside MainWindow, passing coords is straightforward; if created externally, ensure app.py coordinates are passed at creation time.

Estimated effort: 30–90 minutes of focused edits and local verification.

Next action: Task 1 — inspect src/weatherapp/gui/worker.py, src/weatherapp/gui/main_window.py, and src/weatherapp/app.py now and report back with the exact symbols and default coordinates found.
