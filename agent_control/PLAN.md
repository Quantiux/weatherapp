# Implementation Plan

This file is maintained by the agent during the current task.

The plan describes how the task in CURRENT_TASK.md will be completed.

Keep it concise and actionable.

---

## Task Summary

Implement Version-1.2 of WeatherApp: make the MainWindow UI more compact by replacing the vertical stack of weather labels with a two-column QGridLayout. Maintain the existing top row (icon 64×64 + description) and preserve worker threading, manual refresh, and automatic refresh behavior.

---

## Files To Modify

- `src/weatherapp/gui/main_window.py` (replace vertical list with a QGridLayout: add static "name" labels in column 0 and existing value labels in column 1; keep icon QLabel and top row unchanged)
- `src/weatherapp/app.py` (no change expected unless startup wiring requires it)

---

## Implementation Steps

1. Update `agent_control/PLAN.md` (this file) to reflect Version-1.2 work and files to modify.
2. Modify `src/weatherapp/gui/main_window.py`:
   - Import QGridLayout from PyQt6.QtWidgets.
   - Create a QGridLayout containing field name labels in column 0 and the existing value QLabel widgets in column 1, sized compactly.
   - Keep the top row (icon 64×64 and description) as a horizontal layout above the grid.
   - Place the manual refresh button below the grid.
   - Preserve all signal/slot connections, worker threading, and the SVG rendering helper.
3. Run an import check (PYTHONPATH=src) to ensure modules import without raising errors at import time.
4. Update `agent_control/STATE.md` describing the implemented changes and modified files.
5. Run the self-checklist in `agent_control/CHECKLIST.md` and fix any issues found.

---

## Risks or Unknowns

- PyQt6 may not be available in the execution environment; import checks may fail. If so, record this as an environmental limitation in STATE.md and stop after ensuring code changes are correct.
- Layout sizing across different desktop environments may vary; the goal is compactness, not pixel-perfect alignment.

---

## Verification

- Application modules import without errors when PYTHONPATH=src (subject to PyQt6 availability).
- MainWindow displays the icon and description on the top row and weather data in a two-column grid with field names in column 0 and values in column 1.
- Refresh button continues to request a fetch and automatic 10-minute refresh remains intact.
