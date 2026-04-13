# Implementation Plan (Version-4.3)

Goal:

Replace the 7-day forecast grid with a horizontal card-based layout while preserving
existing worker output, formatting helpers, icons, and all other tabs.

Scope & constraints:

- Modify only these files as required:
  - src/weatherapp/gui/main_window.py
  - src/weatherapp/app.py (smoke-test only)
- Do NOT modify: src/weatherapp/gui/worker.py (worker must remain unchanged)
- Keep diffs minimal and localized to the 7-DAY UI block.
- Do not add new dependencies.
- Follow project constraints in CONSTRAINTS.md (no large refactors, no new top-level
  directories, no blocking I/O on GUI thread).

Approach:

- Implement a DayCardWidget (QFrame) used to display a single day's forecast.
  - Internally use QGridLayout with two columns: column 0 labels (left-aligned),
    column 1 values (right-aligned).
  - Reuse existing formatting helpers used in the NOW tab (e.g. _visibility_text,
    _uv_text, icon rendering helpers, time formatting helpers).
  - Fixed card width ~240 px and subtle border to separate cards visually.
- Replace the existing daily_grid/table with a QScrollArea that contains a
  QWidget with a QHBoxLayout and the seven DayCardWidget instances. The scroll
  area should show horizontal scrolling when window width is small.
- Update on_weather_fetched (or equivalent UI update slot) to iterate the
  worker-emitted data['daily'] list and populate each DayCardWidget.
  - Populate up to 7 cards; if fewer items appear, hide unused cards.
  - Preserve icon rendering logic (QSvgRenderer -> QPixmap -> QPainter) and
    description formatting (no space before parenthesis).
- Keep current-weather and hourly tabs unchanged.

Files to modify (exact):

- Modify: src/weatherapp/gui/main_window.py
  - Add DayCardWidget class near other widget definitions (keep import-time
    overhead minimal — use PyQt imports at module level as project does).
  - Replace daily_grid creation code with scroll area + container + HBox
    creation. Pre-create 7 DayCardWidget instances and add them to the HBox.
  - Update the UI update slot to populate DayCardWidget fields using the
    emitted daily dicts.
- Possibly modify: src/weatherapp/app.py for a smoke-launch helper (no
  behavior changes). Prefer no edits if not required.

Task breakdown:

Task 1: Inspect current UI code

Objective: Find exact locations in main_window.py that build the 7-DAY UI and
identify variable/widget names used for daily widgets and update slot(s).

Steps:
1. Open src/weatherapp/gui/main_window.py and locate the 7-DAY tab construction
   and the on_weather_fetched slot (or similarly named handler).
2. Record widget variable names for daily grid and any helper methods.
3. Note where icon rendering and formatting helpers are defined or imported.

Verification: import check:
PYTHONPATH=src python -c "import weatherapp"

Task 2: Implement DayCardWidget

Objective: Add a small reusable widget class representing a day's card.

Steps:
1. Create DayCardWidget(QFrame) with a QGridLayout (labels left, values right).
2. Create QLabel placeholders for required fields: Date, icon+desc, Tmax, Tmin,
   Humid_max, Cloud_max, Rain_tot, Snow_tot, Precip_max, Wind_max, Gusts_max,
   Vis_min, UV_max, Sunrise, Sunset. Use the same keys the worker emits.
3. Add a method populate_from_dict(d) that safely formats and sets label texts
   and sets the icon pixmap using existing rendering helpers (defensive try/except).
4. Set fixed width ~240 and apply QFrame.StyledPanel or stylesheet border.

Task 3: Replace daily grid with scrollable horizontal cards

Objective: Replace existing grid/table with QScrollArea -> container -> QHBoxLayout
and insert 7 DayCardWidget instances.

Steps:
1. Remove or comment out the daily_grid construction; add a QScrollArea in its
   place with horizontal scroll policies and no vertical scroll.
2. Create container QWidget/QFrame with QHBoxLayout; add 7 DayCardWidget widgets.
3. Add the container to the scroll area and ensure size policies keep card width
   fixed while allowing horizontal scrolling.
4. Ensure spacing and margins match the NOW tab visual rhythm.

Task 4: Populate cards from worker data

Objective: Update the UI handler that receives worker data to populate DayCardWidget
instances using data['daily'].

Steps:
1. After existing hourly update logic, check for data.get('daily').
2. Iterate daily items up to 7 and call card.populate_from_dict(daily[i]).
3. Hide any unused cards when fewer than 7 items are present.
4. Ensure updates occur on the GUI thread (slot is already called on GUI thread).

Task 5: Validation & safety checks

Objective: Ensure app imports and runs without regressions; no blocking I/O.

Steps:
1. Run: PYTHONPATH=src python -c "import weatherapp" — fix any import errors.
2. If PyQt6 is available, run: PYTHONPATH=src python -m weatherapp.app and
   manually confirm:
   - 7-day tab shows 7 bordered cards arranged horizontally in a scroll area.
   - Each card shows icon, description, and fields formatted like NOW tab.
   - Horizontal scrolling works when window width is small.
3. Verify no duplicated widgets or rows.
4. Spot-check resizing behavior.

Task 6: Update agent_control/STATE.md

Objective: Record what was implemented, which files changed, and any
limitations (e.g., PyQt6 not present in CI).

Steps:
1. Add Version: 4.3 with a concise description of the card-based 7-day UI.
2. List modified files and any known limitations.

Task 7: Self-review using agent_control/CHECKLIST.md

Objective: Run the checklist and fix issues.

Steps:
1. Verify only required files were modified.
2. Ensure PEP8 (line length <= 100) for new code.
3. Confirm no blocking calls on the GUI thread.

Acceptance criteria (Success):

- App imports successfully.
- 7-day forecast displays as seven card widgets in a horizontal scroll area.
- Each card is a bordered box with internal grid layout for labels/values.
- Worker-emitted daily data populates cards correctly; icons render as before.
- Horizontal scrolling works and layout is stable when resizing.

Risks & mitigations:

- Risk: Widget names differ and moving widgets could break signal/slot links.
  Mitigation: Prefer creating new DayCardWidget instances and populating them
  rather than moving existing widgets. Do not alter worker signals.
- Risk: Visual regressions. Mitigation: Keep changes confined to 7-DAY block and
  match spacing/alignment from NOW tab.

Estimated effort: 1–2 hours local edits and verification.

Next action: implement Task 1 (inspect src/weatherapp/gui/main_window.py) now.
