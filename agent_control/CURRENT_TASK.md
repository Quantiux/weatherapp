# Current Task

Implement Version-4.5 of WeatherApp.

Goal:
Improve Version-4.4 GUI to display current time and today's date above description field of current weather.

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

#### NOW Tab:

- Current time (in %l:%M %P format) and today's date (in %b %d %Y (%a) format), separated by comma ',', should be displayed above the SVG icon and description field. Example: " 3:45 PM, Sep 15 2024 (Sun)".
- Current time and date should be styled with a smaller font size than the description field, and should be left-justified.
- Time and date should auto-update with auto-refresh and upon clicking "Refresh Now" button.

#### HOURLY Tab:

- No changes required

#### 7-DAY Tab:

- No changes required

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
