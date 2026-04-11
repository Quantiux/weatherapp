# Implementation Plan (Version-3)

This plan implements the CURRENT_TASK.md Version-3 requirements: extend the GUI to display current weather (unchanged), 24-hour hourly forecast (existing), and a new 7-day daily forecast block beginning tomorrow.

Keep changes minimal and limited to files named in CURRENT_TASK.md.

---

## Task Summary

Implement Version-3 of WeatherApp: add a 7-day daily forecast block below the existing hourly forecast while preserving the current-weather layout and styling. Worker must emit daily forecast data (next 7 days starting tomorrow) including sunrise and sunset times.

---

## Files To Modify

- `src/weatherapp/gui/main_window.py` — add UI block for the 7-day forecast, 15-column grid, rendering SVG icons at 24×24, formatting date/weekday and sunrise/sunset per spec, defensive updates on missing fields.
- `src/weatherapp/gui/worker.py` — extend the `weather_fetched` payload to include a `daily` key: list[dict] with 7 items (tomorrow → +6). Each dict must include fields in the exact display order.
- `src/weatherapp/app.py` — no functional change expected; may be used to smoke-test the app.

Do not modify other modules listed as protected in CONSTRAINTS.md.

---

## Worker changes (src/weatherapp/gui/worker.py)

- Extend the dict emitted by `weather_fetched` to include a "daily" key whose value is a list of 7 plain dicts (one per day), starting with tomorrow.
- Each daily dict fields (string keys) and expected types (display order):
  1. "Date": string (e.g. "04-11(Sat)") — date formatted MM-DD(WeekdayAbbrev) with NO space before the opening parenthesis.
  2. "svg": string (svg filename, relative to src/weatherapp/icons)
  3. "description": string (short human description)
  4. "Temp": numeric
  5. "Feels": numeric
  6. "Humidity": numeric (percent)
  7. "Cloud cover": numeric (percent)
  8. "Rainfall": numeric (inches)
  9. "Snowfall": numeric (inches)
 10. "Precip.": numeric (percent)
 11. "Wind": numeric (mph)
 12. "Gusts": numeric (mph)
 13. "Visibility": numeric (miles)
 14. "UV": numeric
 15. "Sunrise": string (ISO or epoch accepted — MainWindow will format to 12-hour AM/PM without seconds)
 16. "Sunset": string (same as Sunrise)

- Keep existing threading model, signal names (`weather_fetched`, `fetch_failed`) and behavior. Do not modify protected data modules. Convert/format minimal values if worker already provides equivalents; otherwise pass raw values and let MainWindow handle presentation.

---

## MainWindow changes (src/weatherapp/gui/main_window.py)

- Add a header label: "7-day forecast:" placed below the hourly forecast area (which must remain unchanged).
- Create a 15-column grid layout with column headers in this exact order: Date, Description, Temp, Feels, Humidity, Cloud cover, Rainfall, Snowfall, Precip., Wind, Gusts, Visibility, UV, Sunrise, Sunset.
- Render SVG icons at 24×24 pixels to the left of the parentheted description text. The description text must be parenthesized immediately after the icon filename with no space (e.g., "wi-cloudy.svg(overcast)"). Use QSvgRenderer → QPixmap → QLabel.setPixmap; on error, clear the icon QLabel and still show the text.
- Dates: display as MM-DD(AbbrevWeekday) with no space before the parenthesis (e.g., "04-11(Sat)").
- Sunrise/Sunset: display in 12-hour format with AM/PM, no seconds, and no space between time and AM/PM (e.g., "7:01AM", "8:10PM").
- Layout: present 7 rows (one per day). Use a scroll area only if necessary to avoid disturbing existing layout; preserve responsiveness and avoid blocking the Qt main thread.
- Ensure all UI updates happen on the Qt main thread (in the `on_weather_fetched` handler) and are defensive against missing or partial data.

---

## Testing & Validation

- Import check: `PYTHONPATH=src python -c "import weatherapp"` to ensure no import-time errors.
- If PyQt6 is missing, note this limitation in `agent_control/STATE.md` and skip runtime GUI checks.
- If available, run `python -m weatherapp.app` to visually verify the new 7-day block, icon rendering, and formatting rules.
- Verify the Refresh button triggers a fetch that updates both hourly and daily displays.
- Confirm auto-refresh continues to run every 10 minutes using the existing mechanism.

---

## Data contract (worker → GUI)

`weather_fetched` will emit a dict including the new key:

- "daily": list[dict] with 7 entries (tomorrow → +6 days). Each dict will contain keys listed above in the Worker changes section. The MainWindow will perform final formatting (dates, times, percent signs, units).

Rationale: keep payload simple and serializable; let MainWindow handle display specifics.

---

## Risks and Notes

- PyQt6 may not be available in the execution environment; runtime verification may be skipped and recorded in STATE.md.
- Preserve current-weather widgets exactly; ensure minimal diffs and avoid touching protected modules.
- If the worker already contains daily fields in data/get_weather_data.py, prefer exposing them without heavy conversion.

---

## Next steps

1. Proceed to implement `src/weatherapp/gui/worker.py` changes to emit `daily` payload and include sunrise/sunset.
2. Implement UI changes in `src/weatherapp/gui/main_window.py` to render the 7-day forecast block per spec.
3. Run import checks and, if possible, launch the app for visual verification.
4. Update `agent_control/STATE.md` with what was changed and any limitations.

Proceed now? (yes/no)
