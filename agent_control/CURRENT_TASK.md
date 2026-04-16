# Current Task

Implement Version-5.3 of WeatherApp.

Goal:
Improve Version-5.2 GUI so the vertical spacing between data fields under the 7-DAY tab is decreased.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments to maintain clarity:

`src/weatherapp/gui/main_window.py`
`src/weatherapp/gui/worker.py`
`src/weatherapp/app.py`

Worker requirements:

- Version 5.2 worker already accurately emits all data and no modification is necessary.

MainWindow UI requirements:

- Data fields under the NOW and HOURLY tabs should remain unchanged from Version 5.2.

- Date and description fields under the 7-DAY tab should remain unchanged from Version 5.2.

- Vertical spacing between the remaining fields under the 7-DAY tab should be decreased to match that of those under NOW tab.

Success criteria

- App launches without UI regressions
- Tabs correctly display existing UI sections
- No duplicated forecast rows or widgets
- All data updates correctly in all tabs
- Layout remains stable when resizing
