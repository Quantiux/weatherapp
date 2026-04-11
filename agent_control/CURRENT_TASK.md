# Current Task

Implement Version-4.1 of WeatherApp.

Goal:
Improve Version-4 GUI so the tab names are displayed in bigger fonts.

## Requirements

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

### Worker requirements

- Worker remains unchanged
- Must continue emitting:
  - current weather
  - hourly forecast
  - daily forecast
- No structural changes required

### MainWindow UI requirements

- Tab names "NOW", "HOURLY" and "7-DAY" should be displayed prominently, in bigger font.
- No other UI elements should be modified.

## Implementation Constraints (IMPORTANT)

- Do NOT recreate forecast or daily widgets
- Do NOT duplicate layout logic
- Keep signal/slot logic unchanged

## Success criteria

- App launches without UI regressions
- Tabs correctly display existing UI sections
- No duplicated forecast rows or widgets
- All data updates correctly in all tabs
- Layout remains stable when resizing
