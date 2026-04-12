# Implementation Plan (Version-4.2)

Goal:

Improve Version-4.1 GUI to implement Version-4.2 layout requirements: combine related fields into single rows/columns across the NOW, HOURLY, and 7-DAY tabs while preserving existing widgets, data flow, responsiveness, and worker behavior.

Scope & constraints:

- Modify only these files as required:
  - src/weatherapp/gui/main_window.py
  - src/weatherapp/gui/worker.py (only if strictly required — CURRENT_TASK.md states worker should remain unchanged)
  - src/weatherapp/app.py (smoke-test only)
- Do NOT modify protected modules (see CONSTRAINTS.md).
- Keep diffs minimal and localized to widget/layout adjustments.
- Do not add new dependencies.

Architecture & approach:

- Make only UI layout changes in main_window.py: combine display QLabel/QGrid placements so pairs of related fields appear in a single row/column as specified by CURRENT_TASK.md.
- Preserve existing widget instances where possible (move/adjust them rather than recreate) to avoid duplicated widgets or broken signal/slot connections.
- Ensure all GUI updates continue to occur on the main thread; do not change worker threading or network calls.

Files to modify (exact):

- Modify: src/weatherapp/gui/main_window.py
  - Tasks will target the UI construction sections for NOW tab, HOURLY tab, and 7-DAY tab.
- Possibly modify: src/weatherapp/gui/worker.py
  - Only if necessary to preserve widget reuse; aim for no changes.
- Use src/weatherapp/app.py to run a local smoke launch.

Task breakdown (bite-sized, TDD-style where applicable):

Task 1: Inspect current UI code

Objective: Find the exact locations in main_window.py that create/lay out the NOW, HOURLY, and 7-DAY UI sections.

Files:
- Read: src/weatherapp/gui/main_window.py

Steps:
1. Open the file and locate the sections that build the NOW grid (labels for Temperature, Feels like, Wind, Gusts, etc.).
2. Locate the 24-hour forecast table/scroll area code for HOURLY.
3. Locate the 7-day forecast container for 7-DAY.
4. Note exact variable/widget names used for each label (e.g. self.temp_label, self.feels_label). If names are not obvious, record the grid positions.

Commands:
- python - <<EOF
from pathlib import Path
print(Path('src/weatherapp/gui/main_window.py').read_text()[:1000])
EOF
(used locally; agent will read files programmatically as needed)

Task 2: Update NOW tab layout

Objective: Combine "Temperature" and "Feels like" into one row/label group, and "Wind" and "Gusts" into one row.

Files:
- Modify: src/weatherapp/gui/main_window.py

Steps:
1. Identify the QLabel/QGrid placement for Temperature and Feels like.
2. Replace two separate grid cells with a single combined QLabel or container that renders "Temperature|Feels like: {temp} | {feels}". Prefer updating existing QLabel text assignment rather than creating new widgets.
3. Repeat for Wind and Gusts.
4. Preserve any style, alignment, icons, spacing used previously.
5. Run import check.

Small code example (copy/paste-ready — adapt variable names found in Task 1):

# Example: combine two labels into one
# locate where values are set, then replace with:
self.temp_feels_label = self.temp_feels_label if hasattr(self, 'temp_feels_label') else QLabel()
self.temp_feels_label.setText(f"Temperature|Feels like: {temp_str}|{feels_str}")
# place into grid at the original Temperature cell
parent_grid.addWidget(self.temp_feels_label, row, col)

Verification:
- PYTHONPATH=src python -c "import weatherapp" (no import errors)
- If environment supports PyQt6, run: PYTHONPATH=src python -m weatherapp.app and visually verify NOW tab matches example.

Task 3: Update HOURLY tab layout

Objective: Combine "Temp" and "Feels" into one column and "Wind" and "Gusts" into one column in the 24-hour forecast rows.

Files:
- Modify: src/weatherapp/gui/main_window.py

Steps:
1. Find the code that constructs each hourly row in the scroll area (factory function or loop creating per-hour widgets).
2. Modify the per-row widget creation so the Temp and Feels values are rendered in a single widget or column (e.g. "47°F|39°F").
3. Similarly combine Wind and Gusts into a single text cell.
4. Ensure widths/alignments don't overflow; prefer setting elide modes or fixed widths consistent with existing styling.

Verification:
- Import check
- Visual verification of the HOURLY tab: no duplicated rows, combined columns show values in the requested format.

Task 4: Update 7-DAY tab layout

Objective: Combine Tmax|Tmin, Wind_max|Gusts_max, Sunrise|Sunset columns for each daily row.

Files:
- Modify: src/weatherapp/gui/main_window.py

Steps:
1. Locate the daily-forecast row builder.
2. Replace separate Tmax/Tmin cells with a single combined cell rendering "Tmax|Tmin {tmax}|{tmin}" or the exact example format.
3. Combine Wind_max and Gusts_max in the same way, and Sunrise/Sunset.
4. Preserve icons and description cells.

Verification:
- Import check
- Visual verification of the 7-DAY tab

Task 5: Sanity checks and GUI safety

Objective: Ensure no new blocking calls or thread-safety issues introduced.

Steps:
1. Verify no network calls were moved into the GUI code.
2. Confirm all updates to QLabel text occur on the main thread (where they were before).
3. Run the existing app entrypoint if PyQt6 is available.

Commands:
- PYTHONPATH=src python -c "import weatherapp"
- PYTHONPATH=src python -m weatherapp.app

Task 6: Update agent_control/STATE.md

Objective: Document what was changed, which files were modified, and any limitations (e.g., environment lacking PyQt6).

Files:
- Modify: agent_control/STATE.md

Steps:
1. Add Version: 4.2 and a brief description of the layout changes.
2. List modified files and any known limitations.

Task 7: Self-review using CHECKLIST.md

Objective: Run through the self-review checklist and fix any issues found.

Steps:
1. Verify only required files were touched.
2. Verify PEP8 (line length <= 100). Make small, localized formatting fixes if needed.
3. Ensure no blocking I/O on the GUI thread.

Acceptance criteria (Success):

- App imports successfully (PYTHONPATH=src python -c "import weatherapp").
- When runnable with PyQt6, the NOW, HOURLY, and 7-DAY tabs show combined fields as specified and update correctly when data refreshes.
- No duplicated widgets or forecast rows.
- Layout remains stable when resizing.

Risks & mitigation:

- Risk: Widget variable names differ from plan assumptions and moving widgets could break signal/slot connections. Mitigation: prefer updating text on existing widgets rather than deleting/creating; if rename is unavoidable, reattach signals after changes.
- Risk: Visual regressions on different platforms. Mitigation: keep changes minimal and only change textual composition and grid placements.

Estimated effort: 1–2 hours of focused edits and local verification (less if variable names are obvious and widgets are reused).

Next action: implement Task 1 (inspect src/weatherapp/gui/main_window.py) and record the exact widget names/lines to be modified. Proceed? (yes/no)
