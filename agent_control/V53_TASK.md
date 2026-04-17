# Current Task

Implement Version 5.3 — City/ZIP Name Geocoding (Non-Breaking Upgrade)

## 🎯 Objective

Allow users to enter, instead of raw latitude/longitude (as it is currently implemented):

- City name (e.g., Ann Arbor)
- City + State (e.g., Ann Arbor, MI)
- ZIP code (e.g., 48108)
- PIN code (e.g., 713205)

Lat/lon entry must continue to work exactly as in Version 5.2.

This version introduces geocoding but **does not yet** implement the following features:

- Multiple saved locations
- Persistent configuration
- Map-based selection
- UI redesign beyond minimal additions

## Requirements

Constraint priority rule:
`CONSTRAINTS.md` overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

## 🧱 Architectural Constraints

- Worker threading model must remain unchanged.
- `Worker.fetch()` must still accept `(lat, lon)` only.
- No blocking network calls in GUI thread.
- Geocoding must be performed in the worker thread.
- GUI must remain responsive at all times.
- Existing lat/lon functionality must not regress.

## 🖥 UI Changes (Minimal + Clean)

Modify the existing Location row (above tab bar):

Current version 5.2:

```
Location: [lat] [lon] [Apply]
```

Version 5.3:

```
Location: [Location Input Field................] [Apply]
          (auto-detects city/ZIP or lat,lon)
```

**Replace:**

- `self.lat_input`
- `self.lon_input`

**With:**

- `self.location_input = QLineEdit()`

Keep:

- `Apply` button

## 🧠 Input Behavior Rules

When `Apply` is pressed:

1. Trim input.

2. If input matches pattern:

```
float , float
```

- → Treat as lat/lon (existing behavior)

3. Otherwise:

- → Treat as location query string
- → Send to Worker for geocoding

## 🛰 Geocoding Implementation

**Add to Worker:**

New slot:

```python
@pyqtSlot(str)
def set_location_query(self, query: str) -> None:
```

New internal helper inside Worker:

```python
def _geocode_location(self, query: str) -> tuple[float, float]:
```

**Requirements:**

- Use Open-Meteo Geocoding API (or equivalent free API)
- Must:
  - Return first reasonable match
  - Extract latitude + longitude
  - Raise exception on failure
- Must handle:
  - No results
  - Network failure
  - Invalid input

## 🔁 Flow

When user presses Apply:

**GUI:**

- If lat/lon → call `set_coords(lat, lon)`
- Else → emit new signal:

  ```
  request_geocode.emit(query)
  ```

**Worker:**

1. `_geocode_location(query)`
2. Update `self.coords`
3. Emit `weather_fetched` after normal fetch

## 📡 New Signals

In MainWindow:

```python
request_geocode = pyqtSignal(str)
```

Connect:

```python
self.request_geocode.connect(self._worker.set_location_query)
```

Worker logic:

```
set_location_query →
    geocode →
    update coords →
    fetch()
```

## 🚨 Error Handling

If geocoding fails:

Worker emits:

```
fetch_failed("Location not found")
```

GUI behavior remains unchanged:

- Show QMessageBox
- Do not crash
- Do not clear current weather

## 🔍 Validation Rules

- Empty input → warning dialog
- Invalid numeric format → handled by fallback
- Latitude range: -90 to 90
- Longitude range: -180 to 180

## 📦 Deliverables

Hermes must:

1. Refactor Location row to single QLineEdit
2. Add geocoding capability in Worker
3. Add signal wiring
4. Preserve all Version-5.2 functionality
5. Ensure no blocking calls in GUI thread
6. Ensure no regression in:
   - Hourly forecast
   - Daily forecast
   - Timezone handling
   - Auto-refresh

## 🧪 Manual Test Cases

Test inputs:

```
Ann Arbor
Ann Arbor, MI
New York
48104
42.2509,-83.6694
```

Failure cases:

```
asldkfjalskdfj
999999999
(empty)
```

## 🛑 Explicit Non-Goals (for 5.3)

Do NOT implement:

- Saving multiple locations
- Dropdown history
- Config persistence
- Map UI
- UI redesign beyond input swap
- Location label prettification

Those belong to 5.4–5.6.

## 💡 Design Philosophy for 5.3

This is a **plumbing version**, not a polish version.

We are expanding capability while:

- Preserving threading integrity
- Preserving separation of concerns
- Avoiding UI bloat
- Avoiding architectural drift
