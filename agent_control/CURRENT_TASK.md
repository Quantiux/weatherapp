# 📝 Version 5.9 — List Management (Delete & Clear)

## 🎯 Objective

Empower the user to manage their saved locations by adding functionality to delete individual entries or wipe the entire history, including safety confirmations.

## 🛠 Requirements

1. **Expand `ConfigManager`** (`src/weatherapp/config_manager.py`)
   Add two methods to handle data removal:
   - `remove_location(location_name: str)`: Removes the specific string from the `saved_locations` list and updates the JSON file.
   - `clear_all_locations()`: Resets the `saved_locations` list to an empty list and updates the JSON file.

2. **UI implementation** (`src/weatherapp/gui/main_window.py`)
   Add management buttons to the "Saved" layout:
   - **Delete Button:** Add a button labeled "Delete" (or a 🗑️ icon).
     - **Behavior:** It should target the item currently displayed in the `saved_locations` dropdown.
     - **Confirmation:** Trigger a `QMessageBox.question`: _"Are you sure you want to delete this location? This action cannot be undone."_ with "Yes/No" options.
   - **Clear All Button:** Add a button labeled "Clear All".
     - **Behavior:** Wipes the entire list.
     - **Confirmation:** Trigger a `QMessageBox.warning` with "Yes/No" buttons: _"This will delete all saved locations. This action cannot be undone. Proceed?"_

3. **State Refresh & Selection Logic**
   - After a **Delete**:
     - Update the dropdown list.
     - If the deleted item was the one currently shown, switch the dropdown display to the first available item or a blank state.
   - After a **Clear:**
     - Empty the dropdown immediately.
     - Ensure the "Set Default" and "Save" buttons remain functional for the current search input.

## 🧪 Success Criteria

1. Selecting "Ann Arbor" and clicking "Delete" removes it from the list and the config file.
2. Clicking "Clear All" results in an empty dropdown.
3. The app does **not** crash if the user tries to delete from an empty list (handle the edge case).
4. No location is actually removed until the user clicks "Yes" on the confirmation dialog.
