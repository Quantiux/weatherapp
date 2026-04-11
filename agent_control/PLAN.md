# Implementation Plan (Version-4)

This plan implements the CURRENT_TASK.md Version-4 requirement: refactor the Version-3 GUI into a tab-based interface using QTabWidget. This is a UI architecture refactor only — data fetching, worker logic, and display/formatting rules from Version-3 must remain unchanged.

Keep changes minimal and limited to files named in CURRENT_TASK.md.

---

## Task Summary

Implement Version-4 of WeatherApp: replace the root QVBoxLayout structure with a QTabWidget and move existing UI sections into three tabs in this order: NOW, HOURLY, 7-DAY. Do not recreate or duplicate forecast widgets or layout logic; move the existing containers into tabs.

---

## Files To Modify

- `src/weatherapp/gui/main_window.py` — refactor root layout to use QTabWidget and move the current-weather, 24-hour forecast, and 7-day forecast containers into separate tabs. Preserve all existing widgets, grids, QScrollArea structures, and signal/slot connections.
- `src/weatherapp/gui/worker.py` — only modify if required for widget reuse (CURRENT_TASK.md restricts changes; none expected).
- `src/weatherapp/app.py` — no functional change expected; may be used to smoke-test the app.

Do not modify other modules listed as protected in CONSTRAINTS.md.

---

## Refactor Notes

- Move (not recreate) the existing top_row/current info grid/refresh button into the NOW tab.
- Move the existing 24-hour forecast scroll area into the HOURLY tab.
- Move the existing 7-day forecast scroll area into the 7-DAY tab.
- Ensure tab order is NOW → HOURLY → 7-DAY and the default selected tab is NOW.
- Keep all QScrollArea usage intact; preserve responsiveness and avoid blocking the Qt main thread.
- Do not alter the worker thread, signal names, or auto-refresh behavior.

---

## Testing & Validation

- Import check: `PYTHONPATH=src python -c "import weatherapp"` to ensure no import-time errors.
- If PyQt6 is missing, note this limitation in `agent_control/STATE.md` and skip runtime GUI checks.
- If available, run `python -m weatherapp.app` to visually verify the tabs and that each tab shows the existing UI sections without duplication.
- Verify the Refresh button triggers a fetch that updates all tabs simultaneously.

---

## Risks and Notes

- This is a layout refactor only; avoid touching protected modules.
- Keep diffs minimal and maintain backward compatibility with Version-3 display behavior.

---

## Next steps

1. Implement the QTabWidget refactor in `src/weatherapp/gui/main_window.py`.
2. Run import checks and, if possible, launch the app for visual verification.
3. Update `agent_control/STATE.md` with what was changed and any limitations.

Proceed now? (yes/no)
