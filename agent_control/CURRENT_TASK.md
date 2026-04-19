# Version 5.10 — UI Declutter (Context Menus)

## 🎯 Objective

Relocate **Set Default**, **Delete**, and **Clear All** actions to a right-click context menu on the "Saved Locations" dropdown. This leaves the "Save" button as the only remaining physical button for the saved list, optimizing horizontal space.

## 🛠 Implementation Steps

1.  **UI Refactoring** (`src/weatherapp/gui/main_window.py`)
    - **Remove Buttons:** Delete the code creating `self.set_default_button`, `self.delete_location_button`, and `self.clear_locations_button`.

    - **Enable Context Menu:**

    ```python
    self.saved_locations.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.saved_locations.customContextMenuRequested.connect(self.on_saved_context_menu)
    ```

    - **Update Layout:** The `saved_layout` will now only contain:

    ```
    [Label: "Saved:"] [Dropdown (Stretch)] [Save Button]
    ```

2.  **Implement the Context Menu Handler**
    The menu will now offer three distinct management actions:

    ```python
    def on_saved_context_menu(self, pos):
        """Show a context menu with management actions for the saved list."""
        menu = QMenu(self)
        current_item = self.saved_locations.currentText()

        if current_item:
            # Action 1: Set as Default
            default_action = menu.addAction(f"Set '{current_item}' as Default")
            default_action.triggered.connect(self.on_set_default_clicked)

            # Action 2: Delete
            del_action = menu.addAction(f"Delete '{current_item}'")
            del_action.triggered.connect(self.on_delete_clicked)

            menu.addSeparator()

        # Action 3: Clear All
        clear_action = menu.addAction("Clear All Saved Locations")
        clear_action.triggered.connect(self.on_clear_clicked)

        menu.exec(self.saved_locations.mapToGlobal(pos))
    ```

3.  **Logic Sync**
    - Ensure `on_set_default_clicked` now reads the city from `self.saved_locations.currentText()` (or the input box, since they are synced) and updates the config.

    - Ensure the status message (e.g., "Default set to...") still appears to confirm the action to the user.

## 🧪 Success Criteria

1. **Minimalist UI:** The "Saved" row is now just a label, a dropdown, and a "Save" button.
2. **Ease of Use:** Right-clicking the dropdown provides a clear "management" suite of options.
3. **Stability:** Setting a default from the menu correctly updates config.json and survives a restart.
