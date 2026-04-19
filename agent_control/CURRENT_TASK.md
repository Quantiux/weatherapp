# Version 5.12 — Single-Row Command Bar

## 🎯 Objective

Finalize the location management by moving all controls into a single, high-density row and fixing the context menu responsiveness by decoupling selection from automatic fetching.

## 🛠 Implementation Details

1. **Unified Layout** (`src/weatherapp/gui/main_window.py`)
   - **Container:** A single `QHBoxLayout` for the entire control suite.

   - **Order:**
     1. `QLabel("Location:")`

     2. `self.saved_locations` (`QComboBox`, stretch=1) — _Stretches to fill space_.

     3. `self.location_input` (`QLineEdit`, stretch=2) — _Stretches more to allow for long addresses_.

     4. `self.apply_button` (`QPushButton`)

     5. `self.save_button` (`QPushButton`)

2. **Signal & Context Menu Fix**
   - **Dropdown Selection:** Change `self.saved_locations.currentIndexChanged` to `self.saved_locations.activated`.
     - _Benefit:_ This ensures that right-clicking to open the menu doesn't accidentally trigger a weather fetch if the index happens to shift, and prevents the "fetch-on-startup" loop.
   - **Context Policy:** Ensure `setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)` is set before any signals are connected.

3. **Interaction Flow**
   - **Select from Dropdown:** Automatically fills `location_input` and triggers a fetch.
   - **Type in Input:** User hits "Apply" or "Enter" to fetch.
   - **Right-Click Dropdown:** Opens the management menu immediately.

## 🧪 Success Criteria

1. The entire location interface exists on one line.
2. Right-clicking the dropdown provides management tools.
3. The window width remains manageable due to the removal of the three maintenance buttons.
