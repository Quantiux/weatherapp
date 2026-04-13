# Current Task

Implement Version-4.4 of WeatherApp.

Goal:
Improve Version-4.3 GUI to display date labels, SVG icons and descriptions in daily forecast cards in bigger fonts.

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

- No changes required

#### HOURLY Tab:

- No changes required

#### 7-DAY Tab:

- Date label in each card should be displayed in bold font for better readability.
- In the description label, the SVG icon should be displayed at 48x48 pixels, and the parentheted text should be in bold font.
- In the description label, there should be some space between the icon and the text in the description label.

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
