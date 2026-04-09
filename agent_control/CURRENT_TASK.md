# Current Task

Implement Version-1.1 of WeatherApp.

Goal
Render the weather SVG icon in the GUI instead of displaying the SVG filename.

The worker already emits the icon filename via the "svg" field in the `weather_fetched` payload. The GUI must load the corresponding SVG file and display it visually.

Constraint priority rule:
CONSTRAINTS.md overrides all other instructions.

Files allowed to modify:
`src/weatherapp/gui/main_window.py`
`src/weatherapp/app.py`

Do NOT modify:

`src/weatherapp/gui/worker.py`
`src/weatherapp/data/_`
`src/weatherapp/utils/_`

Icon assets

Weather icon SVG files are located in:

`src/weatherapp/icons/`

Example filenames:

`wi-day-sunny.svg`
`wi-night-clear.svg`
`wi-day-cloudy.svg`

MainWindow UI requirements

The window must display:

• weather icon (rendered SVG image) followed by weather description in parentheses (as in Version-1)
• temperature and other weather values already shown in Version-1

Implementation requirements:

- Add a QLabel dedicated to displaying the icon.
- Load the SVG file referenced by the "svg" field from the worker payload.

Example path resolution:

`src/weatherapp/icons/<svg_filename>`

Use Qt classes to render SVG:

Preferred approach:

- QSvgRenderer
- QPixmap
- QLabel.setPixmap()

Simpler acceptable approach:

- QPixmap if Qt can load the SVG directly.

Icon display requirements

The icon must:

• appear before the weather description (description in parentheses as in Version-1)
• scale to approximately 64×64 pixels
• update whenever new weather data arrives

Behavior:

Inside MainWindow.on_weather_fetched():

1. read svg filename from payload
2. construct icon file path
3. load SVG
4. render into QPixmap
5. set QLabel pixmap

Example logic (conceptual)

icon_file = data["svg"]
icon_path = icons_dir / icon_file
pixmap = QPixmap(str(icon_path))
self.icon_label.setPixmap(pixmap.scaled(64, 64))

Refresh behavior

Icon must update whenever weather data refreshes.

Version-1.1 constraints

No UI redesign.
No styling.
No changes to data layer.
No changes to worker thread logic.

Success criteria

Application launches.

Weather icon is displayed visually (not as filename).

Icon updates when Refresh Now is clicked.

Weather description text remains visible next to the icon in parentheses.
