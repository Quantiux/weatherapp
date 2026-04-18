# 📝 Version 5.6 — Initial Search Polish

## 🎯 Objective

Replace the raw coordinate string (latitude/longitude) in the location bar with a human-readable city name on startup.

## 🛠 Requirements

1. **Update Initialization Logic** (`src/weatherapp/gui/main_window.py`)
   - Locate the `try/except` block in `__init__` that sets the initial text for `self.location_input`.
   - Change the default text from the formatted `DEFAULT_COORDS` string to `"New York"`.
   - **Constraint:** Ensure that if a `last_location` exists in the `config.json` (via `ConfigManager`), that value takes priority over the "New York" default.

2. **Synchronize with Worker**
   - Verify that when the app starts, the `Worker` is initialized with the correct numerical coordinates for New York (which it already is in `worker.py` via `DEFAULT_COORDS`).
   - This ensures the first fetch works immediately, even though the text box shows the name.

## 🧪 Success Criteria

1. On a fresh install (no config), the app opens with "New York" in the search bar.
2. On subsequent launches, the app opens with the last successfully searched city name.
3. The first weather fetch succeeds without the user having to press "Apply".
