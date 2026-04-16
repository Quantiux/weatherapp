# Current Task

Implement Version-5.2 of WeatherApp.

## Objective

Make the **NOW tab time/date display reflect the selected location’s local time**, not the system clock.

Time must update automatically when:

- The app first loads
- The user changes coordinates
- A weather refresh completes
- The 10-second timer fires

## Current Problem

`MainWindow._update_time_label()` uses:

```python
datetime.now()
```

This returns **machine-local time**, not the timezone of the selected coordinates.

However:

- The Worker already extracts `timezone_str` from the API response.
- Hourly and daily forecasts already use this timezone correctly.

The missing piece is passing that timezone to the GUI and using it for the NOW tab clock.

## Required Changes

### 1. Worker: Include timezone in result payload

Inside `Worker.fetch()`, after:

```python
timezone_str = response.Timezone().decode("utf-8")
```

Add to the final `result` dictionary:

```python
result["timezone"] = timezone_str
```

This must always be included when available.

### 2. MainWindow: Store active timezone

In `MainWindow.__init__` add:

```python
self._active_timezone = None
```

### 3. Update timezone when weather is fetched

Inside `on_weather_fetched()`:

```python
tz = data.get("timezone")
if tz:
    try:
        self._active_timezone = ZoneInfo(tz)
    except Exception:
        self._active_timezone = None
```

Import required:

```python
from zoneinfo import ZoneInfo
```

### 4. Modify `_update_time_label()` to use location timezone

Replace:

```python
now = datetime.now()
```

With:

```python
if self._active_timezone:
    now = datetime.now(timezone.utc).astimezone(self.\_active_timezone)
else:
    now = datetime.now()
```

Import:

```python
from datetime import timezone
```

## Exzpected Behavior

| Scenario                 | Time Label Behavior                                 |
| ------------------------ | --------------------------------------------------- |
| App launch               | Shows default location’s local time                 |
| User changes coordinates | After fetch completes, time updates to new location |
| Timer tick               | Time updates in selected location’s timezone        |
| No timezone available    | Fallback to system time (defensive behavior)        |

## Display Format (unchanged)

Format remains:

`9:27 PM, Apr 15 2026 (Wed)`

Rules:

- 12-hour clock
- Leading space for single-digit hour
- AM/PM uppercase
- Date: `%b %d %Y (%a)`

## Architectural Intent

Version-5.2 completes the transition from:
“Weather app running on my machine”

to:
“Weather app representing a real geographic location”

This makes the app logically consistent:

- Hourly forecast → correct timezone
- Daily sunrise/sunset → correct timezone
- NOW tab clock → correct timezone

## Non-Goals (Do NOT change)

- No UI layout changes
- No threading changes
- No additional API calls
- No new dependencies

## Acceptance Criteria

✔ Changing from Ann Arbor to Tokyo changes the clock to JST
✔ Changing from Michigan to California shifts time by 3 hours
✔ Timer keeps updating correctly in selected timezone
✔ No crashes if timezone missing
✔ No regression in hourly/daily formatting
