# Implementation Plan (Version-5.7)

Goal:

Implement Version 5.7 — Custom Default Location: allow the user to set a persistent "default_location" that takes priority at startup over last_location and the hardcoded fallback. Keep changes minimal and focused to the files listed below.

Files to inspect/modify:

- src/weatherapp/config_manager.py  (extend schema: add default_location; add setter/getter methods)
- src/weatherapp/gui/main_window.py  (add "Set Default" button next to the Saved section Save button; wire handler to call ConfigManager.set_default_location and show brief feedback)
- agent_control/STATE.md (update after verification)

Design constraints / notes:

- Follow agent_control/CONSTRAINTS.md: do not modify unrelated modules, do not add new dependencies, keep changes minimal.
- All I/O and network work remains in the worker thread — UI changes are purely configuration and signal emission.
- Persist config via existing ConfigManager JSON file behavior (XDG path fallback). ConfigManager already exists from prior versions.

Acceptance criteria:

1. Config file includes a "default_location" key once a user sets it.
2. At startup the app selects the location in this order:
   a. default_location (if set)
   b. last_location (if present)
   c. "New York" (hardcoded fallback)
3. Clicking "Set Default" saves the visible text from the location input to config.json and displays a short status message (e.g., "Default set to London").
4. User workflow described in CURRENT_TASK.md works end-to-end: set default to London, change last_location by searching Tokyo, restart app -> London is loaded.

Tasks (bite-sized):

Task 1 — Inspect current ConfigManager (5–10 min)

Objective: Confirm existing ConfigManager API and JSON schema location.
Files: src/weatherapp/config_manager.py
Steps:
- Read file to check existing methods: load/save, get_saved_locations, add_location, get_last_location, set_last_location.
- Note how config file path and defaults are implemented so we follow the same style.

Task 2 — Add default_location support to ConfigManager (10–20 min)

Objective: Add get_default_location() and set_default_location(location_name: str) and persist key.
Files: src/weatherapp/config_manager.py
Steps:
- Modify load() to return default_location key when present, defaulting to None.
- Implement set_default_location(location_name: str) that updates in-memory dict and calls save(); swallow errors defensively like existing methods.
- Keep API backward compatible (do not rename existing methods).
- Add type hints and simple docstrings to new methods.

Task 3 — Wire startup priority logic in MainWindow (10–20 min)

Objective: On startup, choose initial displayed location using the priority: default_location -> last_location -> "New York".
Files: src/weatherapp/gui/main_window.py
Steps:
- At initialization where previous code used ConfigManager.get_last_location() or hardcoded fallback, modify to first check ConfigManager.get_default_location().
- If default exists, set the location input text to default and emit the existing request_geocode (or queued fetch) so the worker handles geocode+fetch.
- Preserve existing behavior when default_location is None.

Task 4 — Add "Set Default" button and handler (10–20 min)

Objective: Minimal UI addition — a button (text "Set Default" or a ⭐ icon) next to the existing Save button in the Saved section.
Files: src/weatherapp/gui/main_window.py
Steps:
- Add a QPushButton labeled "Set Default" placed next to the Save button, matching nearby style.
- Connect clicked -> _on_set_default_clicked.
- Implement _on_set_default_clicked to read current location_input text, call ConfigManager.set_default_location(text), and show brief feedback (QStatusBar.showMessage or a small temporary QLabel). Keep feedback non-blocking and brief (2–3 seconds).
- Handle empty input gracefully (show message like "Cannot set empty default").

Task 5 — Validation, import smoke, and local checks (5–15 min)

Objective: Ensure no import-time issues and basic runtime behavior.
Steps:
- Run: PYTHONPATH=src python -c "import weatherapp" to catch import errors.
- If environment allows, run the app locally: PYTHONPATH=src python -m weatherapp.app and manually verify Set Default flow. If not possible, instantiate ConfigManager and MainWindow objects in a small script to ensure methods exist and do not crash on construction.

Task 6 — Update agent_control/STATE.md (5–10 min)

Objective: Record what was changed, files modified, and any known limitations or manual steps for verification.
Files: agent_control/STATE.md
Steps:
- Note added ConfigManager methods
- Note MainWindow changes (button, handler, startup priority change)
- Describe manual validation steps and any environment requirements (PyQt6, display server)

Risks / uncertainties:

- If ConfigManager is implemented differently than expected (different API names or persistence behavior), adapt changes to match existing conventions.
- UI layout collisions: keep the new button placement minimal; if layout is fragile, fallback to placing the button in the status area or next to Saved dropdown.
- Writing to config.json may fail in readonly environments; follow existing defensive pattern (swallow or log errors) — report limitation in STATE.md.

Verification checklist (before finishing):

- [ ] Config file contains "default_location" after using Set Default.
- [ ] Startup priority follows default -> last -> New York.
- [ ] No GUI thread blocking introduced; all network/IO remains in worker thread.
- [ ] Existing Save/Load behavior unchanged when default_location not used.
- [ ] agent_control/STATE.md updated with exact files modified and limitations.

Next action (I'll perform now):

1. Inspect src/weatherapp/config_manager.py and src/weatherapp/gui/main_window.py to confirm exact insertion points and adapt code to existing patterns.
2. Implement ConfigManager additions and MainWindow UI changes in minimal diffs.
3. Run import smoke checks and update STATE.md with results.

Notes/Constraints:

- Do not add external dependencies; use stdlib and PyQt6 only.
- Do not commit or stage changes (per CONSTRAINTS.md); the human will review and commit.
- Keep changes minimal and defensive.
