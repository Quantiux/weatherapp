# Implementation Plan (Version-5.8)

Goal:

Implement Version 5.8 — UI Synchronization & Startup Alignment: ensure the Search input and Saved Locations dropdown always reflect the same startup location and that the initial fetch happens after both widgets are set.

Files to inspect/modify:

- src/weatherapp/gui/main_window.py  (centralize startup_location selection; apply to both widgets; ensure fetch signal emitted after UI update)
- src/weatherapp/config_manager.py  (confirm get_default_location/get_last_location APIs; adapt if names differ)
- agent_control/STATE.md (update after verification)

Design constraints / notes:

- Follow agent_control/CONSTRAINTS.md: modify only files required by this task, keep diffs minimal, do not add dependencies.
- Preserve existing behavior except for the specified synchronization and startup ordering.
- All network/IO remains in worker threads; UI code must not block.

Acceptance criteria:

1. On startup the Search Bar and the Saved Dropdown show the exact same city name (or the Search Bar shows the primary startup name and the Saved dropdown shows that name when present in saved list).
2. Startup location selection priority (centralized):
   a. default_location (if present in config)
   b. last_location (if present)
   c. "New York" (hardcoded fallback)
3. The initial weather fetch corresponds to the city displayed in both widgets and occurs only after both widgets have been set.

Tasks (bite-sized):

Task 1 — Inspect relevant modules (5–10 min)

Objective: Confirm exact APIs and current startup logic.
Files:
- src/weatherapp/gui/main_window.py
- src/weatherapp/config_manager.py

Steps:
- Read MainWindow __init__ to find where last_location/fallback is determined and where UI widgets are populated and where request_fetch is emitted.
- Confirm ConfigManager method names for default/last location retrieval and any related behavior.

Task 2 — Create centralized startup_location logic in MainWindow (10–25 min)

Objective: Compute startup_location once and apply it to both widgets before requesting fetch.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- In __init__, add a single block to determine startup_location using ConfigManager (default -> last -> "New York").
- Apply startup_location to:
  - self.location_input.setText(startup_location)
  - try: self.saved_locations.setCurrentText(startup_location) (handle when startup not in saved list)
- Ensure UI updates occur before emitting self.request_fetch (or request_geocode), so the worker fetches for the displayed location.
- Keep changes defensive: wrap setCurrentText in try/except if the widget API differs.

Task 3 — Verify fetch ordering and signal emission (5–15 min)

Objective: Ensure fetch signal is emitted only after UI elements show the startup location.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- If existing code emits the fetch before setting widgets, reorder so widgets updated first then emit.
- If necessary, use QTimer.singleShot(0, lambda: self.request_fetch.emit()) to defer emission until after event loop processes UI updates (non-blocking).
- Avoid blocking; do not perform any network/IO on the GUI thread.

Task 4 — Basic runtime checks (5–15 min)

Objective: Ensure no import-time errors and basic behavior.
Steps:
- Run: PYTHONPATH=src python -c "import weatherapp" to detect import issues.
- If possible, instantiate MainWindow in a headless check (without showing) to exercise __init__ and ensure no exceptions. If PyQt6/display not available, rely on static inspection and unit-like instantiation with QApplication when possible.

Task 5 — Update agent_control/STATE.md (5–10 min)

Objective: Record what was implemented, which files were changed, and known limitations.
Files:
- agent_control/STATE.md

Steps:
- Note the exact changes to MainWindow and any defensive handling added.
- Describe verification performed and any remaining manual checks (PyQt6/display requirement).

Risks / uncertainties:

- If MainWindow or ConfigManager use different method names than expected, adapt to the existing API.
- Saved dropdown widget behavior: setCurrentText may raise or be ignored if value not present — handle gracefully.
- In environments without a display server, full runtime GUI verification cannot be completed here; document this in STATE.md.

Verification checklist (before finishing):

- [ ] Startup location computed once and applied to both widgets.
- [ ] Initial fetch occurs after widgets are updated.
- [ ] No blocking I/O on GUI thread.
- [ ] agent_control/STATE.md updated with files changed and limitations.

Next actions (I'll perform now):

1. Inspect src/weatherapp/gui/main_window.py and src/weatherapp/config_manager.py to confirm insertion points and adapt code to match existing patterns.
2. Implement minimal changes in main_window.py to centralize startup_location and reorder fetch emission if needed.
3. Run import smoke checks and update STATE.md with results.

Notes/Constraints:

- Do not add external dependencies; use stdlib and PyQt6 only.
- Do not stage or commit changes; human will review and commit.
- Keep changes minimal and defensive.
