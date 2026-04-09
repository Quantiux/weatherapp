# Current Task

Implement Version-1.3 of WeatherApp.

Goal:
Improve typography and visual alignment of the main window without changing data fetching, threading, or application structure.

Requirements:

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Modify these modules only as needed to meet the goal, including docstrings and comments:
`src/weatherapp/gui/main_window.py`

Do not modify any other modules.

Layout improvements:

The layout structure from Version-1.2 must remain:

- Top row: icon + weather description
- Two-column grid: weather data fields
- Refresh button at bottom

Icon improvements:

- Render the SVG icon at a smaller size (approximately 48x48).
- Ensure the icon is horizontally aligned with the description text.
- Prevent icon distortion.

Description text:

- Increase the font size of the weather description.
- Make the description visually prominent relative to data fields.
- Keep parentheses around the description text.

Grid typography:

Improve readability of the data grid:

- Slightly increase font size of value labels.
- Keep field names left-aligned.
- Keep values right-aligned.

Spacing:

Improve spacing for clarity:

- Add small spacing between icon and description.
- Ensure the grid rows are evenly spaced.

Constraints:

Do not change:

- Worker thread logic
- Weather data structure
- Worker signals
- Networking code
- Refresh timer behavior

Success criteria

- Application launches successfully.
- SVG icon appears smaller and aligned with description text.
- Description text is visually prominent.
- Weather data grid is easier to read.
- No functional behavior changes.
