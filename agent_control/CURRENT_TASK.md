# Version 5.10 — UI Declutter (Context Menus)

## 🎯 Objective

Relocate **Set Default**, **Delete**, and **Clear All** actions to a right-click context menu on the `saved_locations` dropdown. This leaves the "Save" button as the only primary physical action, maximizing horizontal space and fixing the startup widget sync.

## 🛠 Implementation Steps

1.  **UI Refactoring** (`src/weatherapp/gui/main_window.py`)
    - **Remove Buttons:** Delete the instances of `self.set_default_button`, `self.delete_location_button`, and `self.clear_locations_button`.

    - **Refactor Layout:** Simplify the `saved_layout` to include only:

    ```
    [Label: "Saved:"] [Dropdown (Stretch)] [Save Button]
    ```

    - **Enable Context Menu:**

    ```python
    self.saved_locations.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.saved_locations.customContextMenuRequested.connect(self.on_saved_context_menu)
    ```

2.  **Context Menu Implementation**
    Add the `on_saved_context_menu` handler to provide management options:
    - ⭐ **Set Default:** Configures the currently selected city as the `default_location`.
    - 🗑️ **Delete:** Removes the current city from the list (with confirmation).
    - 🧹 **Clear All:** Wipes the entire saved history (with confirmation).

3.  **Startup Synchronization (The "Hermes Fix")**
    Update the `__init__` constructor to ensure the search box and dropdown are perfectly aligned on launch:
    1. Read `default_location` (fallback to `last_location`, then "New York").
    2. Set `self.location_input.setText(city)`.
    3. Populate `self.saved_locations` and use `setCurrentText(city)` to ensure both match immediately.

## 🧪 Success Criteria

1. **Minimalist UI:** The "Saved" row no longer causes horizontal window stretching.
2. **Functionality:** Right-clicking the dropdown successfully opens the management menu.
3. **Correct Sync:** The app starts with the search bar and dropdown showing the exact same location.
