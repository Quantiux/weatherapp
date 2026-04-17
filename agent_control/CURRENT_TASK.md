# Current Task

Implement Version 5.4 — Saved Locations + Persistent Configuration

## 🎯 Objective

Allow users to:

- Save locations they frequently check
- Quickly switch between them
- Automatically reload the last used location at startup

Locations should persist between runs using a small configuration file.

This version introduces **persistent configuration**, but **does not yet implement**:

- Map selection
- Weather alerts
- UI theming
- Location reordering
- Cloud sync

## Requirements

Constraint priority rule:
`CONSTRAINTS.md` overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

## 🧱 Architectural Principles

Maintain the existing design rules:

- Worker thread fetches weather
- GUI thread handles UI only
- Worker accepts only `(lat, lon)`
- Geocoding still happens in worker
- GUI never performs network calls

Configuration logic must be **separate from UI and worker logic**.

## 🗄 Configuration Storage

Use a simple JSON file.

**Location**

Linux example:

`~/.config/weatherapp/config.json`

Fallback if directory does not exist:

`~/.weatherapp_config.json`

Example config

```json
{
  "last_location": "Ann Arbor, MI",
  "saved_locations": ["Ann Arbor, MI", "Durgapur, West Bengal", "48104", "731205"],
  "refresh_interval_minutes": 10
}
```

Important:

Locations are stored as **strings**, not coordinates.

Reason:

- Allows geocoding updates
- Keeps config human-readable
- Avoids stale coordinates

## New Module

Create:

```
config_manager.py
```

Responsibilities:

```
load_config()
save_config()
add_location()
remove_location()
set_last_location()
```

Example interface:

```python
class ConfigManager:

    def load(self) -> dict:
        ...

    def save(self, config: dict) -> None:
        ...

    def add_location(self, location: str) -> None:
        ...

    def remove_location(self, location: str) -> None:
        ...
```

## 🖥 UI Changes

Add a **Saved Locations dropdown**.

Location row becomes:

```
Location: [Dropdown ▼] [Location Input Field........] [Apply] [Save]
```

### Components

Add:

```
self.saved_locations = QComboBox()
self.save_location_button = QPushButton("Save")
```

Behavior:

Dropdown selection → fills input field.

## User Interaction Flow

### Selecting a saved location

1. User chooses item from dropdown
2. Input field updates
3. Weather fetch triggered

### Saving a location

User flow:

1. Enter location in input
2. Press **Save**

Behavior:

- Add to config JSON file
- Update dropdown
- Avoid duplicates

### Apply button

Same behavior as Version 5.3:

```
lat,lon → direct fetch
text → geocode → fetch
```

Also update:

```
last_location
```

## Startup Behavior

On application launch:

1. Load config
2. Populate dropdown with saved locations
3. If `last_location` exists:
   - populate input
   - automatically fetch weather

If config file does not exist:

- Create default config

## Error Handling

Cases:

**Invalid location**

Worker emits:

```
fetch_failed("Location not found")
```

Do not store invalid locations.

**Config corruption**

If JSON fails to load:

1. Backup corrupted file:

   ```
   config.json.bak
   ```

2. Create fresh config

## Internal Data Flow

GUI:

```
Apply clicked
↓
check format
↓
lat/lon → set_coords
text → request_geocode
```

Worker:

```
set_location_query
↓
\_geocode_location
↓
update coords
↓
fetch()
```

Config updates occur **only in GUI layer**.

Worker must remain stateless regarding config.

## Deliverables

Hermes must implement:

1. `config_manager.py`
2. Persistent JSON configuration
3. Saved locations dropdown
4. Save button
5. Startup auto-load
6. Last location restore
7. Duplicate prevention

No changes allowed to:

- Worker threading model
- Weather fetch logic
- Forecast display logic

## Manual Test Cases

### Persistence

Run app:

```
Enter: Ann Arbor
Save
Close app
Restart
```

Expected:

```
Dropdown contains Ann Arbor
Weather loads automatically
```

### Duplicate protection

```
Save "Ann Arbor"
Save "Ann Arbor"
```

Expected:

```
Only one entry
```

### Invalid location

```
Save: asldkfjalskdfj
```

Expected:

```
Error message
Not saved
```

## Non-Goals (Version 5.4)

Do NOT implement:

- location reordering
- deleting locations from dropdown
- map UI
- weather alerts
- tray icon
- dark/light themes

## Strategic Outcome

After Version 5.4 the app gains:

- Real usability
- Persistence
- Quick switching
- Clean config structure

At this point WeatherApp transitions from **tool → product prototype**.
