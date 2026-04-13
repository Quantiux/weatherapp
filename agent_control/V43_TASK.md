# Current Task

Implement Version-4.3 of WeatherApp.

Goal:
Improve Version-4.2 GUI by replacing the grid layout of 7-day forecast with a horizontal card-based layout.

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

No changes to current weather or hourly forecast display.

#### 7-DAY tab

Reformat the 7-day forecast display.

The current implementation shows the daily forecast in a **table/grid with rows and columns**.
This must be replaced with a **card layout where each day forecast appears in its own box**.

### Layout requirements

- Each forecast day must appear in a **separate rectangular box (card)**.
- Cards are arranged **horizontally in a row** inside a scrollable container.
- Each card displays the forecast for one day.

Use a structure similar to:

QScrollArea  
 └── QWidget container  
 └── QHBoxLayout  
 ├── DayCardWidget (day 1)  
 ├── DayCardWidget (day 2)  
 ├── DayCardWidget (day 3)  
 ├── ...  
 └── DayCardWidget (day 7)

### Card contents

#### Card internal layout

Each DayCard must use a grid layout similar to the layout used in the NOW tab.

Use a `QGridLayout` with two columns:

Column 0: label text  
Column 1: value text

Example structure inside each card:

Date
[icon] (description)

Tmax | Tmin: <value> | <value>
Humid_max: <value>
Cloud_max: <value>
Rain_tot: <value>
Snow_tot: <value>
Precip_max: <value>
Wind_max | Gusts_max: <value> | <value>
Vis_min: <value>
UV_max: <value>
Sunrise | Sunset: <value> | <value>

### Implementation rules

- Worker output and data structure remain unchanged.
- The `daily` list emitted by Worker must still populate the UI.
- Replace the existing `daily_grid` implementation with a **card-based layout**.
- Cards should use QFrame with a subtle border to visually separate each day.
- Use `QGridLayout` inside the `DayCardWidget` for the metrics section.
- Labels aligned left.
- Values aligned right.
- Reuse the same formatting helpers used in the NOW tab.
- Row spacing and alignment should visually match the NOW tab layout.
- Each card should be fixed width (approx 220–260 px) so seven cards fit in a horizontal scroll area.
- Preserve existing icon rendering logic.
- Preserve existing formatting helpers (`_visibility_text`, `_uv_text`).

### Do not change

- Worker code
- data structures
- API fields
- signal/slot logic

## Success criteria

- App launches without UI regressions
- No duplicated forecast rows or widgets
- All data updates correctly in all tabs
- Layout remains stable when resizing
- 7-day forecast is displayed as seven forecast cards instead of a table
- Each day appears in its own bordered box
- Cards are arranged horizontally
- Horizontal scrolling works if window width is small
- Worker data populates the cards correctly
