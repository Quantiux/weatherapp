# Version 5.11 — Single-Row Consolidation

## 🎯 Objective

Refactor the location and saved list management into a single, highly efficient horizontal row.

## 🛠 Requirements

1. **Layout Refactoring** (`src/weatherapp/gui/main_window.py`)
   - **Horizontal Consolidation:** Replace the multiple layout rows with a single `QHBoxLayout` (e.g., `control_bar`).

   - **Widget Order:**
     1. `QLabel("Location:")`

     2. `self.saved_locations` (`QComboBox`, stretch=1) — _Contains the context menu_.

     3. `self.location_input` (`QLineEdit`, stretch=2) — _The primary search box_.

     4. `self.apply_button` (`QPushButton`)

     5. `self.save_button` (`QPushButton`)

2. **Synchronized Interaction Logic**
   - **Dropdown Selection:** When an item is selected in the dropdown, it must immediately update the text in `self.location_input`.
   - **Save Logic:** When "Save" is clicked, it takes the text from `self.location_input`, adds it to the config and the dropdown, and updates the UI.
   - **Context Menu:** Retain the right-click menu on the `saved_locations` dropdown for **Set Default**, **Delete**, and **Clear All**.

3. **Startup Alignment (The "Hermes Fix")**
   - Ensure the `__init__` constructor identifies the startup city (Default → Last → NYC).
   - Set both the dropdown and the text input to this city before the first fetch.

## 🧪 Success Criteria

1. The entire location interface exists on one line.
2. Right-clicking the dropdown still provides management tools.
3. Changing the dropdown selection changes the text in the input box.
4. The window width remains manageable due to the removal of the three maintenance buttons.
