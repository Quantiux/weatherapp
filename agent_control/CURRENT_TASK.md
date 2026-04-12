# Current Task

Implement Version-4.2 of WeatherApp.

Goal:
Improve Version-4.1 GUI for better display of current weather and hourly and 7-day forecast.

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

#### NOW tab

- Combine "Temperature" and "Feels like" fields in one row, without any space before and after "|". Example: "Temperature|Feels like: 49°F|42°F".
- Combine "Wind" and "Gusts" fields in one row, without any space before and after "|". Example: "Wind|Gusts: 10mph|24mph".
- Preserve existing grid layout and styling.

#### HOURLY tab

- Combine "Temp" and "Feels" fields in one column. Example: "Temp|Feels 47°F|39°F".
- Combine "Wind" and "Gusts" fields in one column. Example: "Wind|Gusts 10mph|24mph".

#### 7-DAY tab

- Combine "Tmax" and "Tmin" fields in one column. Example: "Tmax|Tmin 47°F|39°F".
- Combine "Wind_max" and "Gusts_max" fields in one column. Example: "Wind_max|Gusts_max 10mph|24mph".
- Combine "Sunrise" and "Sunset" fields in one column. Example: "Sunrise|Sunset 6:58AM|8:12PM".

## Example layout:

wi-cloudy.svg (overcast)
Temperature|Feels like: 49°F|42°F
Humidity: 62%
Cloud cover: 100%
Rainfall: 0.0in
Snowfall: 0.0in
Precip.: 7%
Wind|Gusts: 10mph|24mph
Visibility: Clear
UV Index: Low

24-hour forecast:
Time Description Temp|Feels Humidity Cloud cover Rainfall Snowfall Precip. Wind|Gusts Visibility UV
9:00AM wi-cloudy.svg(overcast) 47°F|39°F 64% 100% 0.0in 0.0in 7% 9mph|18mph Clear Low
10:00AM wi-cloudy.svg(overcast) 50°F|43°F 62% 100% 0.0in 0.0in 7% 11mph|25mph Clear Low
11:00AM wi-cloudy.svg(overcast) 50°F|44°F 66% 100% 0.0in 0.0in 4% 8mph|25mph Clear Low
12:00PM wi-cloudy.svg(overcast) 59°F|53°F 59% 100% 0.0in 0.0in 4% 11mph|30mph Clear Moderate

7-day forecast:
Date Description Tmax|Tmin Humid_max Cloud_max Rain_tot Snow_tot Precip_max Wind_max|Gusts_max Visib_min UV_max Sunrise|Sunset
04-12(Sun) wi-cloudy.svg(overcast) 79°F|41°F 72% 100% 0.0in 0.0in 20% 21mph|35mph Clear Moderate 6:58AM|8:12PM
04-13(Mon) wi-day-sprinkle.svg(light drizzle) 79°F|60°F 90% 100% 0.0in 0.0in 55% 13mph|31mph Clear High 6:56AM|8:13PM
04-14(Tue) wi-day-showers.svg(slight rain showers) 77°F|63°F 89% 100% 0.0in 0.0in 68% 21mph|40mph Clear Moderate 6:54AM|8:14PM
04-15(Wed) wi-day-rain.svg(moderate rain showers) 69°F|59°F 97% 100% 0.0in 0.0in 68% 19mph|37mph Fair High 6:53AM|8:15PM

## Success criteria

- App launches without UI regressions
- Tabs correctly display existing UI sections
- No duplicated forecast rows or widgets
- All data updates correctly in all tabs
- Layout remains stable when resizing
