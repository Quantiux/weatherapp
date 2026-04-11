# Current Task

Implement Version-1.2 of WeatherApp.

## Goal

Make the UI more compact and readable by replacing the vertical stack of weather labels with a **two-column grid layout**.

## Constraint priority rule

`CONSTRAINTS.md` overrides all other instructions.

## Files allowed to modify

Only modify these modules if required:

- `src/weatherapp/gui/main_window.py`
- `src/weatherapp/app.py`

Do **not** modify other modules.

## Layout requirements

### Top row

Keep the existing horizontal layout:

Icon (64×64) + weather description in parentheses.

### Weather data layout

Replace the current vertical list of labels with a **QGridLayout**.

The grid must have:

- Column 0: field name label
- Column 1: value label

Fields to display:

1. Temperature (Feels like)
2. Humidity
3. Cloud cover
4. Rainfall
5. Snowfall
6. Precipitation probability
7. Wind (Gusts)
8. Visibility
9. UV index

Example structure:

Temperature 62°F (Feels like: 56°F)
Humidity 53%
Cloud cover 79%
Rainfall 0.00 in
Snowfall 0.00 in
Precip 21%
Wind 15.2 mph (Gusts: 31.5 mph)
Visibility 71.8 mi
UV index 1

### Window sizing

The UI should become more compact than Version-1.1.

## Behavior requirements

Keep existing functionality unchanged:

- Worker thread model
- Weather fetch signal
- SVG icon rendering
- Refresh Now button
- 10-minute automatic refresh

## Version-1.2 constraints

- No styling or themes
- No new dependencies
- No networking changes
- No forecast views

## Success criteria

- Application launches successfully
- Weather icon still renders
- Weather data appears in a **two-column grid**
- Refresh button continues to work
