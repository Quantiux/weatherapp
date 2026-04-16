# Implementation Plan (Version-5.2)

Goal:

Make the NOW tab clock reflect the selected location's local time (using the
timezone provided by the weather API) instead of the machine/system clock.

Architecture / Approach:

- Keep changes minimal and localized to the Worker (ensure timezone is in the
  fetch result) and MainWindow (store active timezone, use it for the NOW tab
  clock). No UI layout, threading, or new dependencies.

Files to modify (exact):

- src/weatherapp/gui/worker.py  (add timezone to result payload)
- src/weatherapp/gui/main_window.py  (store active timezone; update handler and
  _update_time_label)
- agent_control/STATE.md (update after implementation)

Assumptions:

- Worker.fetch() already extracts timezone_str from the API response (see
  CURRENT_TASK.md). We will add that value to the result dict as result["timezone"].
- MainWindow already has on_weather_fetched(data) or equivalent handler that
  receives the result payload from Worker.fetch(). We'll update that handler to
  set an active ZoneInfo instance when timezone string is available.

Acceptance criteria (from CURRENT_TASK.md):

- NOW tab clock shows the location's local time on app launch, after coordinate
  change, after a refresh completes, and on the 10s timer ticks.
- Falls back to system time if timezone is missing or invalid.
- No UI layout changes, no threading changes, no new deps.

Step-by-step Tasks (bite-sized):

Task 1 — Inspect code (read-only)

Objective: Locate exact symbols and handlers to change
Files:
- src/weatherapp/gui/worker.py
- src/weatherapp/gui/main_window.py

Steps:
1. Open worker.py: find where timezone_str is decoded and where result dict is
   assembled. Note variable names and where result is emitted.
2. Open main_window.py: find on_weather_fetched (or equivalent) and
   _update_time_label() implementations, the timer that updates the NOW tab, and
   the signal wiring for receiving worker results.

Deliverable: exact function/class/variable names to edit and a one-line note of
current behavior.

Task 2 — Worker: include timezone in result

Objective: Ensure the Worker always returns timezone when available.
File: src/weatherapp/gui/worker.py

Steps:
1. Locate the place timezone_str is extracted (e.g. timezone_str = response.Timezone().decode("utf-8")).
2. Immediately before assembling/returning/emitting result, add:

   result["timezone"] = timezone_str

   - If timezone_str may be None or empty, only add when truthy.
   - Keep the rest of fetch() unchanged (no refactor).
3. Run import check to ensure no syntax errors.

Task 3 — MainWindow: store active timezone

Objective: MainWindow keeps an active ZoneInfo (or None) and updates it when
new weather arrives.
File: src/weatherapp/gui/main_window.py

Steps:
1. In MainWindow.__init__ add:

   self._active_timezone = None

   and add import: from zoneinfo import ZoneInfo
   (also add `from datetime import timezone` if needed by _update_time_label).
2. In on_weather_fetched(data) (or the handler that receives worker results):

   tz = data.get("timezone")
   if tz:
       try:
           self._active_timezone = ZoneInfo(tz)
       except Exception:
           self._active_timezone = None

   - Do this before any code that relies on the clock so the next timer tick
     and any immediate UI update use the new timezone.
3. After updating _active_timezone, call/ensure _update_time_label() runs so the
   NOW tab immediately refreshes to the new timezone (many implementations update
   UI after on_weather_fetched; if not, call it explicitly).

Task 4 — Update _update_time_label() to use timezone

Objective: Use the active timezone for the clock display, fallback to system
clock when None.
File: src/weatherapp/gui/main_window.py

Steps:
1. Replace datetime.now() with:

   if self._active_timezone:
       now = datetime.now(timezone.utc).astimezone(self._active_timezone)
   else:
       now = datetime.now()

2. Ensure imports include: from datetime import datetime, timezone
3. Keep existing formatting code unchanged (12-hour, leading space, AM/PM, date
   format `%b %d %Y (%a)`).
4. Ensure the timer that triggers _update_time_label (10s) continues to call
   this method unchanged.

Task 5 — Smoke & import checks

Objective: Verify no import-time errors and object construction works.

Steps:
- Run: PYTHONPATH=src python -c "import weatherapp"
- Run a small construction check:

PYTHONPATH=src python - <<'PY'
from weatherapp.gui.worker import Worker
from weatherapp.gui.main_window import MainWindow
w = Worker()
# construct MainWindow without starting event loop
mw = MainWindow()
print(mw._active_timezone)
PY

Expected: no import errors; mw._active_timezone is None (or a ZoneInfo if the
worker sets defaults at startup).

Task 6 — Update agent_control/STATE.md

Objective: Record Version-5.2 changes, modified files, verification steps, and
known limitations (e.g., ZoneInfo availability on Python versions prior to 3.9).

Task 7 — Self-review & checklist

- Run through agent_control/CHECKLIST.md manual items (PEP8 ≤100 chars,
  no blocking GUI thread, only required files changed).
- Do NOT stage or commit changes (CONSTRAINTS.md).

Testing / Validation (acceptance):

- Unit-ish smoke: construct Worker and MainWindow and simulate a worker result
  with data={"timezone": "Asia/Tokyo"} calling the on_weather_fetched handler
  to confirm mw._active_timezone becomes ZoneInfo("Asia/Tokyo") and the
  formatted time label updates.
- Manual: run the app locally with PyQt6 and verify: app launch shows default
  location time, changing coordinates and waiting for fetch updates the time.

Risks & Mitigations:

- Risk: Worker does not reliably include timezone_str. Mitigation: defensive
  checks in on_weather_fetched; fallback to system time.
- Risk: timezone string from API may be unknown to ZoneInfo. Mitigation: try/except
  and fallback to None.
- Risk: Python versions before 3.9 lack zoneinfo. Mitigation: project targets
  modern Python; document as limitation in STATE.md if relevant.

Estimated effort: 20–60 minutes.

Next action: Task 1 — inspect the two source files now and report the exact
symbols and insertion points found. After that I'll implement the edits for
Task 2–4 and run the smoke checks described above.
