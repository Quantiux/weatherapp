# Implementation Plan (Version-5.5)

Goal:

Implement Version 5.6 — Initial Search Polish: On startup, the location input should display a human-readable name rather than raw coordinates. Follow CURRENT_TASK.md which requires preferring `last_location` from ConfigManager or falling back to "New York". Keep changes minimal: only modify initialization logic in src/weatherapp/gui/main_window.py.

Files to inspect/modify:

- src/weatherapp/gui/worker.py  (ensure set_location_query and _geocode_location are implemented; handle errors via fetch_failed)
- src/weatherapp/gui/main_window.py  (ensure single free-form input exists, request_geocode signal connected to worker.set_location_query, Apply button emits numeric path or geocode request)
- agent_control/STATE.md (update after verification)

Acceptance criteria:

1. Inputs like "Miami, FL", "Miami, Florida", "Bardhaman, WB", and "Kolkata, West Bengal" resolve to coordinates and trigger a normal weather fetch.
2. Numeric "lat,lon" inputs continue to work unchanged.
3. GUI thread performs no network I/O.
4. On geocode failure the worker emits fetch_failed("Location not found" or friendly message) and the GUI shows an error dialog without crashing.

Tasks (bite-sized):

Task 1 — Load and verify context (done).

Task 2 — Smoke import check
- Run: PYTHONPATH=src python -c "import weatherapp"
- Expected: no import-time heavy failures

Task 3 — Verify worker implementation
- Confirm Worker.set_location_query exists and performs geocoding with urllib, updates self.coords, and calls fetch().

Task 4 — Verify MainWindow wiring
- Confirm self.location_input exists, request_geocode signal is defined, Apply button emits request_geocode for non-numeric inputs, and connections to worker exist.

Task 5 — Manual smoke run (if environment allows):
- Start the app in the project environment and try applying "Miami, FL" to ensure the UI updates as expected. If running interactive UI is not possible, run a focused integration sanity: instantiate Worker and call set_location_query in a thread-like context (non-GUI run) and observe no exceptions.

Task 6 — Update agent_control/STATE.md with findings and next steps.

Next action (I'll perform now):
1. Write this PLAN.md (done).
2. Run the smoke import check (PYTHONPATH=src python -c "import weatherapp").

Notes/Constraints:
- Do not add dependencies. Use urllib from the stdlib for geocoding HTTP requests.
- Do not commit changes automatically; the human operator will review and commit.
- Keep diffs minimal and restricted to the files listed above.
