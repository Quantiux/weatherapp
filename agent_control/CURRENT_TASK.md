# Current Task

Implement Version-5.0 of WeatherApp.

Goal:
Remove hard-coded coordinates from the Worker and allow the GUI to dynamically provide latitude and longitude for weather requests.

This prepares the application for future UI features allowing users to change location.

## Requirements

Constraint priority rule:
`CONSTRAINTS.md` overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

- `src/weatherapp/gui/main_window.py`
- `src/weatherapp/gui/worker.py`
- `src/weatherapp/app.py`

### Worker Requirement

The Worker must support **dynamic coordinates provided by the GUI**.

#### Required behavior

1. Worker must no longer rely on a hard-coded coordinate inside `fetch()`.
2. Worker should store coordinates as an instance attribute:

   ```python
   self.coords
   ```

3. Worker must expose a slot allowing the GUI to update coordinates.

   Example concept:

   ```python
   @pyqtSlot(float, float)
   def set_coords(self, lat, lon)
   ```

   This method should update `self.coords`.

4. `fetch()` must always use the **latest value of** `self.coords` when calling:

   ```python
   `fetch_weather(self.coords)`
   ```

5. Default coordinates should remain available so the app launches normally if the GUI has not yet set a location.

### MainWindow Requirements

No visible UI changes in this version.

However the GUI must be prepared to control the worker location.

#### Requirements

MainWindow must store current coordinates:

```python
self.coords
```

When the refresh button is clicked:

1. MainWindow must pass the stored coordinates to the worker
2. Worker then fetches weather for those coordinates

Example flow:

```python
MainWindow → worker.set_coords(...)
MainWindow → worker.fetch()
```

The existing refresh workflow must remain unchanged except for passing coordinates.

## App Initialization

Application startup must:

1. Initialize default coordinates
2. Pass them to the Worker before the first fetch
3. Launch the first weather fetch normally

## Implementation Constraints (IMPORTANT)

- Do NOT redesign the Worker threading model
- Do NOT modify signal names
- Do NOT change returned weather data structures
- Do NOT change forecast parsing logic
- Keep worker network logic untouched except for coordinates
- Do NOT introduce new modules

## Success Criteria

- App launches normally
- Weather loads exactly as before
- Coordinates are no longer hard-coded inside fetch()
- GUI can update Worker coordinates
- Refresh still works
- No UI regressions
