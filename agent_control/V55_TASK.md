# WeatherApp – CURRENT TASK

Version: 5.5

## Objective

Fix geocoding failures for location queries containing commas or state/region
qualifiers (e.g., "Miami, FL", "Miami, Florida", "Bardhaman, WB").

Currently only single-token city names (e.g., "Miami", "Bardhaman") resolve
successfully.

The GUI layer is functioning correctly and must remain unchanged.

---

## Scope of Changes

Modify the Worker geocoding implementation so that:

1. Location queries containing commas and spaces are handled correctly.
2. The full user input string is preserved and passed to the geocoding API.
3. The query string is properly URL encoded before constructing the request URL.
4. If multiple results are returned by the geocoder, the first valid result
   should be used.
5. Error handling should remain consistent with the existing `fetch_failed`
   signal.

---

## Expected Behavior

The following inputs should resolve successfully:

- `Miami`
- `Miami, FL`
- `Miami, Florida`
- `Bardhaman`
- `Bardhaman, WB`
- `Kolkata, West Bengal`

After geocoding:

- Worker updates coordinates
- Weather fetch proceeds normally
- UI updates as in previous versions

---

## Constraints

Do NOT modify:

- GUI layout or widgets
- location dropdown/save functionality
- configuration file structure
- threading architecture

Only modify the geocoding logic in the worker.

---

## Files Likely Affected

`src/weatherapp/gui/worker.py`

---

## Acceptance Criteria

1. Entering `Miami, FL` fetches weather successfully.
2. Entering `Miami, Florida` fetches weather successfully.
3. Entering `Bardhaman, WB` fetches weather successfully.
4. Entering `Kolkata, West Bengal` fetches weather successfully.
5. Existing inputs (`Miami`, `Detroit`) continue to work.
6. No regressions in saved location functionality.
