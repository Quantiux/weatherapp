# 📝 Version 5.7 — Custom Default Location

## 🎯 Objective

Allow the user to designate a specific location as their "Home" or "Startup" location, overriding the default behavior.

## 🛠 Requirements

1. **Configuration Schema Update**
   - Add a `default_location` key to `config.json`.
   - **Logic Priority at Startup:**
     1. `default_location` (User-set preference).
     2. `last_location` (Most recent successful search).
     3. `"New York"` (Hardcoded fallback).

2. **Expand `ConfigManager`** (`src/weatherapp/config_manager.py`)
   - Add `set_default_location(location_name: str)`: Saves the string to the `default_location` key.
   - Add `get_default_location() -> Optional[str]`: Retrieves the value.

3. **UI implementation** (`src/weatherapp/gui/main_window.py`)
   - **"Set Default" Button:** Add a button labeled "Set Default" (or a ⭐ icon) next to the "Save" button in the "Saved" section.
   - **Functionality:** Clicking this button takes the current text in the location input and saves it as the `default_location` in the config.
   - **Visual Feedback:** Show a brief status message (e.g., "Default set to London") in a `QStatusBar` or a small temporary label.

## 🧪 Success Criteria

- User searches "London", clicks "Set Default", and closes the app.
- User then searches "Tokyo" (which updates `last_location`).
- Upon restart, the app loads **London** because it is the explicit default.
