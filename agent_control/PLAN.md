# Implementation Plan (Version-5.11)

Goal:

Implement Version 5.11 — Single-Row Consolidation: refactor the location controls into a single horizontal control bar and ensure the saved-dropdown and free-form input remain synchronized, preserve the context menu, and ensure startup alignment (Default -> Last -> "New York").

Files to inspect/modify:

- src/weatherapp/gui/main_window.py  (consolidate Saved + Location into one QHBoxLayout; remove fixed widths in favor of stretch; keep worker wiring and context menu)
- agent_control/STATE.md (update after verification)

Design constraints / notes:

- Follow agent_control/CONSTRAINTS.md: modify only files required by this task, keep diffs minimal, do not add dependencies.
- Preserve existing behavior: network/IO stays in worker thread; signals/slots remain as-is.
- Keep changes defensive (try/except around config access and setCurrentText) and maintain existing attribute names where reasonable to minimize diffs.

Acceptance criteria:

1. The entire location interface exists on a single horizontal row with widget order:
   - QLabel("Location:")
   - self.saved_locations (QComboBox, stretch=1)
   - self.location_input (QLineEdit, stretch=2)
   - self.apply_location_button (QPushButton)
   - self.save_location_button (QPushButton)
2. Right-clicking the dropdown still shows Set Default / Delete / Clear All.
3. Selecting an item in the dropdown immediately updates the text in the input and triggers the Apply flow.
4. Startup priority preserved and both widgets are set to the startup city before the first fetch (Default -> Last -> "New York").

Tasks (bite-sized):

Task 1 — Inspect current implementation (5–10 min)

Objective: Locate the existing location rows and startup logic in MainWindow.__init__.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- Identify the block that creates the saved_row and loc_row and where they are added to main_layout.
- Confirm existing signal/slot wiring for apply/save and saved_locations.activated.

Task 2 — Replace with single control bar (10–30 min)

Objective: Replace the two separate rows with a single QHBoxLayout (control_bar) in the same position in the layout.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- Remove setFixedWidth calls for saved_locations and location_input.
- Create control_bar = QHBoxLayout() and add widgets in the required order using stretch factors for saved_locations (1) and location_input (2).
- Replace main_layout.addLayout(saved_row); main_layout.addLayout(loc_row) with main_layout.addLayout(control_bar).
- Keep all existing handlers (apply/save/context menu) intact and ensure they reference the same attributes.

Task 3 — Verify interaction logic (5–15 min)

Objective: Ensure dropdown selection updates the input and triggers apply; Save updates config and dropdown.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- Ensure saved_locations.activated handler sets location_input text and clicks Apply.
- Ensure _save_location uses ConfigManager.add_location and calls _populate_saved_locations().
- Keep context menu handler on_saved_context_menu unchanged.

Task 4 — Startup Alignment (Hermes Fix) (5–15 min)

Objective: Ensure startup_location is computed once and applied to both widgets before emitting the initial fetch/geocode.
Files:
- src/weatherapp/gui/main_window.py

Steps:
- Preserve existing startup logic block but ensure control_bar widgets are set before QTimer.singleShot(...) emission.
- Use QTimer.singleShot(0, ...) to defer the fetch so UI updates are processed.

Task 5 — Basic runtime checks (5–15 min)

Objective: Ensure no import-time errors and basic behavior.
Steps:
- Run: PYTHONPATH=src python -c "import weatherapp" to detect import issues.
- If possible, instantiate MainWindow in a headless check; otherwise rely on static inspection.

Task 6 — Update agent_control/STATE.md (5–10 min)

Objective: Record what was implemented, files changed, and limitations.
Files:
- agent_control/STATE.md

Steps:
- Document exact edits to MainWindow and mention any defensive handling.
- Note verification steps performed and any remaining manual UI checks required.

Risks / uncertainties:

- setCurrentText may be ignored if startup location is not present in the combobox — treat the input as the single visible source of truth.
- Headless environments cannot exercise context menu behavior; document this in STATE.md.

Verification checklist (before finishing):

- [ ] Single-row control bar created with the specified widget order and stretch.
- [ ] Context menu preserved and functional.
- [ ] Dropdown selection updates input and triggers Apply.
- [ ] Startup location applied to both widgets before the first fetch.
- [ ] Import smoke check passes.
- [ ] agent_control/STATE.md updated.

Next actions (I'll perform now):

1. Edit src/weatherapp/gui/main_window.py to replace the two-row location editor with the single-row control bar and remove the fixed widths.
2. Run import smoke checks: PYTHONPATH=src python -c "import weatherapp".
3. Update agent_control/STATE.md with a concise summary of changes and verification results.

Notes/Constraints:

- Do not add external dependencies; use stdlib and PyQt6 only.
- Do not stage or commit changes; human will review and commit.
- Keep edits minimal and defensive.
