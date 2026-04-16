# Current Task

Implement Version-5.1 of WeatherApp.

## Goal

Add a **user-editable location selector** so WeatherApp can fetch weather data for arbitrary coordinates instead of the fixed default location.

The worker already supports dynamic coordinates (Version-5.0).
This version adds **GUI controls and signal wiring** to allow users to update them.

UI appearance and weather display behavior remain unchanged except for the new location controls.

## Requirements

Constraint priority rule:
`CONSTRAINTS.md` overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

- `src/weatherapp/gui/main_window.py`
- `src/weatherapp/gui/worker.py`
- `src/weatherapp/app.py`

### 1. Location Input Controls

Add a small location editor in the top control area of the main window, above the tab bar.

Recommended layout:

Location: [Latitude ______] [Longitude ______] [Apply]

Fields:

- Latitude (float)
- Longitude (float)
- Apply button

Behavior:

- Fields initialize with the default coordinates
- Pressing **Apply** updates the worker coordinates and triggers a fetch

### 2. Coordinate Validation

Accept values only if:

-90 ≤ latitude ≤ 90
-180 ≤ longitude ≤ 180

If invalid:

- Do not update worker coordinates
- Do not trigger a fetch
- Optionally show a brief status message

### 3. Update Flow

When the user presses **Apply**:

GUI
↓
read latitude/longitude fields
↓
validate values
↓
update `self.coords`
↓
`worker.set_coords(lat, lon)`
↓
emit `request_fetch`

Weather refresh should occur immediately after applying new coordinates.

### 4. Preserve Existing Behavior

The following must remain unchanged:

- Worker thread architecture
- Networking code
- Data parsing
- Weather display widgets
- Refresh timer
- Manual refresh button

Periodic refresh should automatically use the **latest coordinates**.

## Implementation Notes

### MainWindow additions

Add attributes:

`self.coords`
`self.lat_input`
`self.lon_input`
`self.apply_location_button`

Add method:

`_apply_new_location()`

Responsibilities:

read inputs
validate
update coords
call `worker.set_coords()`
emit `request_fetch`

### Suggested Widget Types

Use:

`QLineEdit`
`QPushButton`
`QHBoxLayout`

Optional improvement:

`QDoubleValidator`

to enforce numeric input.

## Initial State

Coordinates should initialize from the existing default:

`DEFAULT_COORDS = (42.2509, -83.6694)`

Populate the input boxes with these values when the UI loads.

## Files Expected to Change

`src/weatherapp/gui/main_window.py`

No changes required in:

- `src/weatherapp/gui/worker.py`
- data structures
- thread setup

## Acceptance Criteria

The feature is complete when:

1. User can enter new latitude and longitude
2. Clicking Apply triggers a weather refresh
3. Worker fetch uses the new coordinates
4. Periodic refresh continues using the new location
5. Invalid coordinates are rejected
6. Existing UI layout remains stable

## Out of Scope (Future Versions)

The following features are intentionally excluded:

- City name search
- Geocoding APIs
- Map-based location selection
- Saving multiple locations
- Persistent configuration

These may be considered in later versions.
