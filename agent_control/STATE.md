# Project State

This file records the current development state of the WeatherApp project.

It is updated by the agent after completing each task.

---

## Current Version

Version: 2.2

Description:
Version-2.2 updates the MainWindow UI to display current weather (unchanged layout/styling) and a 24-hour hourly forecast starting with the hour after the current hour. Wind and gust values are rounded to the nearest integer in both current and forecast displays. These changes are display/data-shaping only and do not affect worker threading, networking, or data structures beyond the worker emitting a trimmed hourly payload.

---

## Implemented Features

- Worker now emits an "hourly" key containing the next 24 hourly forecast items starting with the hour after the current hour.
- Wind and Gusts values are rounded to the nearest integer in both current weather and hourly forecast displays.
- The MainWindow forecast UI shows 24 rows under the header "24-hour forecast:" and preserves existing current-weather layout and styling.

---

## Files Modified

- `src/weatherapp/gui/worker.py` (rounded wind/gusts values and trimmed hourly payload to next 24 hours)
- `src/weatherapp/gui/main_window.py` (display rounded wind/gusts values; forecast area now shows 24 rows with header "24-hour forecast:")

---

## Known Limitations

- PyQt6 may not be installed in the execution environment; import or runtime checks requiring PyQt6 could fail. This is an environment limitation rather than a code error.
- Rendering and exact layout depend on platform font metrics; aim is functional alignment and readability rather than pixel-perfect appearance.
- If the data-layer response structure changes, the Worker falls back to omitting or trimming the hourly key; MainWindow handles missing or shorter hourly lists gracefully.

---

## Next Planned Features

1. Add unit tests for visibility and UV mapping functions.
2. Add visual regression snapshots for the forecast area in CI if a headless Qt environment is available.

---

## Notes for Future Development

- Keep lazy imports in the Worker to preserve GUI importability for testing.
- MainWindow updates should continue to run on the GUI thread only.
