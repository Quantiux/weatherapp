# Implementation Plan (Version-5.0)

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
