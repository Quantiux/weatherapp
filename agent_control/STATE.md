# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 3.0

Description:
Version-3 extends the GUI to include a 7-day daily forecast block below the existing 24-hour hourly forecast and current weather fields. The worker now emits a "daily" payload (7 entries starting tomorrow) including sunrise and sunset ISO timestamps. The MainWindow renders daily rows in a 15-column grid with Date, Description (icon + parenthetical text), Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip., Wind, Gusts, Visibility, UV, Sunrise, Sunset. Sunrise/Sunset are displayed in 12-hour AM/PM format without seconds and with no space before AM/PM (e.g., "7:01AM"). SVG icons for daily descriptions are rendered at 24×24 pixels.

---

## Implemented Features

- Worker now emits a "daily" key containing a list of 7 daily forecast items starting with tomorrow. Each item contains Date, svg, description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip., Wind, Gusts, Visibility, UV, Sunrise, Sunset.
- MainWindow now displays a new "7-day forecast:" block below the hourly forecast. The block uses a 15-column grid matching the required header order and renders description icons at 24×24 with parenthetical description text without intervening spaces.
- Sunrise and Sunset times are parsed from ISO strings and formatted to the required 12-hour AM/PM form with no seconds and no space before AM/PM.
- All GUI updates remain on the main thread; the worker threading model and signal names are unchanged.

---

## Files Modified

- `src/weatherapp/gui/worker.py` (added creation of `daily` payload with sunrise/sunset fields)
- `src/weatherapp/gui/main_window.py` (added 7-day forecast UI block, parsing/formatting of daily fields)
- `agent_control/PLAN.md` (updated plan to Version-3)
- `agent_control/STATE.md` (this update)

---

## Known Limitations

- PyQt6 may not be installed in the execution environment; import or runtime checks requiring PyQt6 could fail. This is an environment limitation rather than a code error.
- The worker emits sunrise/sunset in ISO format (or omits them if parsing fails); the MainWindow attempts to parse them but falls back to "--" if parsing fails.
- Rendering and exact layout depend on platform font metrics; aim is functional alignment rather than pixel-perfect appearance.
- New code respects CONSTRAINTS.md: no protected modules were modified, no new dependencies were added, and changes were limited to specified files.

---

## Next Planned Features

1. Add unit tests for daily payload formatting and time parsing.
2. Add error logging around parsing failures to help diagnose data inconsistencies.

---

## Notes for Future Development

- Keep lazy imports in the Worker to preserve GUI importability for testing.
- MainWindow updates should continue to run on the GUI thread only.
