# Current Task: Version 5.6 — Initial Search Polish

## 🎯 Objective

Replace the raw coordinate string (latitude/longitude) in the location bar with a human-readable city name ("New York") on startup.

## 🛠 Requirements

### 1. Update Initialization Logic (`src/weatherapp/gui/main_window.py`)

- Modify the `__init__` block to set the initial text of `self.location_input`.
- **Priority:**
  1. `last_location` from `ConfigManager` (if it exists).
  2. `"New York"` as the hardcoded fallback.
- Remove the code that formats `DEFAULT_COORDS` into the text box.

### 2. Verify Worker Sync

- Ensure the app performs an initial fetch on startup. Since `worker.py` already defaults to New York's coordinates, the first fetch will display New York data immediately while the UI shows the city name.

## 🧪 Success Criteria

1. On first-ever launch, the search bar shows "New York".
2. If the user previously searched for "London", the bar shows "London" on restart.
3. The app loads weather data automatically on startup.
