# Version 5.8 — UI Synchronization & Startup Alignment

## 🎯 Objective

Ensure all location-aware UI elements (Search Input and Saved Locations Dropdown) are perfectly synchronized to the same startup location.

## 🛠 Requirements

1. **Centralize Startup Location Selection** (`src/weatherapp/gui/main_window.py`):
   In the `__init__` method, create a single logic block to determine the `startup_location`:
   1. Check `default_location` from config.
   2. If none, check `last_location` from config.
   3. If none, fall back to `"New York"`.

2. **Synchronize UI Widgets:**
   Apply the `startup_location` to both widgets:
   - `self.location_input.setText(startup_location)`
   - ``self.saved_locations.setCurrentText(startup_location)`
     - Note: If the startup location is not currently in the "Saved" list, the dropdown should ideally show a placeholder or remain blank, but the Search Bar must remain primary.

3. **Update Fetch Logic:**
   Ensure the `self.request_fetch.emit()` signal is only called after both UI elements have been set, ensuring the UI reflects exactly what is being fetched.

## 🧪 Success Criteria

1. On startup, the Search Bar and the "Saved" Dropdown show the exact same city name.
2. If the user has a "Default" set (e.g., Ann Arbor), both boxes show "Ann Arbor" immediately upon launch.
3. The initial weather fetch matches the city displayed in both boxes.
