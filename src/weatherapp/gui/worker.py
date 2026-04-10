"""Background worker module for WeatherApp GUI.

This module provides the Worker QObject used to execute network I/O in a
separate thread. The module avoids importing the heavy data client at
import time to keep the GUI modules importable for tests and static checks.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Import weather fetcher lazily inside fetch() to avoid heavy imports at module import time
# (keeps GUI importable for testing and static analysis).


class Worker(QObject):
    """Background worker that runs in a QThread and fetches weather data.

    The Worker is designed to live in a QObject moved to a QThread. Calls to
    the `fetch` slot are made from the GUI thread via a queued signal; the slot
    executes in the worker thread, performs network I/O, and emits signals to
    notify the GUI of success or failure.
    """

    weather_fetched = pyqtSignal(object)  # emits a dict-like result
    fetch_failed = pyqtSignal(str)  # emits error message

    def __init__(self, coords: tuple[float, float] = (42.250967869842874, -83.66940204731466)) -> None:
        """Initialize the worker with optional coordinates.

        Args:
            coords: Tuple of (latitude, longitude). Defaults to a fixed location
            used for development and testing.
        """
        super().__init__()
        self.coords = coords

    @pyqtSlot()
    def fetch(self) -> None:
        """Fetch weather data and emit signals on completion or failure.

        This method calls the shared data layer function `fetch_weather`. It
        extracts a comprehensive set of current weather fields (matching the
        indices used by the formatter layer) and emits a single dictionary
        containing the parsed values. The method performs imports lazily so
        importing this module doesn't trigger network or heavy third-party
        imports.
        """
        try:
            # Import the data-layer fetcher here to avoid heavy imports at module import time
            from weatherapp.data.get_weather_data import fetch_weather, TIMEZONE
            # lightweight helpers for mapping codes
            from weatherapp.utils.weather_code_mapper import get_svg_for_code, get_desc_for_code

            response = fetch_weather(self.coords)

            result = {}

            try:
                current = response.Current()

                # Indices mirror show_weather.parse_current usage
                temp = float(current.Variables(0).Value())
                rel_humidity = float(current.Variables(1).Value())
                apparent = float(current.Variables(2).Value())
                is_day = bool(current.Variables(3).Value())
                rain_val = float(current.Variables(4).Value())
                showers_val = float(current.Variables(5).Value())
                snowfall = float(current.Variables(6).Value())
                weather_code = int(current.Variables(7).Value())
                cloud_cover = float(current.Variables(8).Value())
                wind_speed = float(current.Variables(9).Value())
                wind_gusts = float(current.Variables(10).Value())
                precip_prob = float(current.Variables(11).Value())
                visibility_m = float(current.Variables(12).Value())
                uv_index = float(current.Variables(13).Value())

                # Combine rain & showers
                rain = rain_val + showers_val

                # Convert visibility meters -> miles (approx)
                visibility_miles = visibility_m * 0.000621371

                # Map icon and description using mapper helpers
                tod = "day" if is_day else "night"
                svg = get_svg_for_code(weather_code, tod)
                desc = get_desc_for_code(weather_code)

                result = {
                    "weather": f"{svg} ({desc})",
                    "temperature_2m": temp,
                    "relative_humidity_2m": rel_humidity,
                    "apparent_temperature": apparent,
                    "is_day": is_day,
                    "rain": rain,
                    "snowfall": snowfall,
                    "cloud_cover": cloud_cover,
                    "wind_speed": wind_speed,
                    "wind_gusts": wind_gusts,
                    "precipitation_probability": precip_prob,
                    "visibility": visibility_miles,
                    "uv_index": uv_index,
                    "weather_code": weather_code,
                    "svg": svg,
                    "description": desc,
                }
            except Exception:
                # Fallback: pass the whole response if structured access fails
                result = {"response": response}

            # Build hourly payload (list of 48 dicts) when available
            try:
                hourly = response.Hourly()
                # Variables indices correspond to get_weather_data params
                temperature = hourly.Variables(0).ValuesAsNumpy()
                relative_humidity = hourly.Variables(1).ValuesAsNumpy()
                apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
                is_day_arr = hourly.Variables(3).ValuesAsNumpy()
                precip_prob_arr = hourly.Variables(4).ValuesAsNumpy()
                weather_code_arr = hourly.Variables(5).ValuesAsNumpy()
                rain_arr = hourly.Variables(6).ValuesAsNumpy()
                showers_arr = hourly.Variables(7).ValuesAsNumpy()
                snowfall_arr = hourly.Variables(8).ValuesAsNumpy()
                cloud_cover_arr = hourly.Variables(9).ValuesAsNumpy()
                visibility_arr = hourly.Variables(10).ValuesAsNumpy()
                wind_speed_arr = hourly.Variables(11).ValuesAsNumpy()
                wind_gusts_arr = hourly.Variables(12).ValuesAsNumpy()
                uv_index_arr = hourly.Variables(13).ValuesAsNumpy()

                # Calculate time labels using Time (start) and Interval
                start_ts = int(hourly.Time())
                interval = int(hourly.Interval())
                # number of points
                length = len(temperature)

                tz = ZoneInfo(TIMEZONE)

                hourly_list = []
                for i in range(length):
                    ts = start_ts + i * interval
                    dt = datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(tz)
                    # Format like "10:00 AM"
                    try:
                        time_label = dt.strftime("%-I:%M %p")
                    except Exception:
                        # Fallback for environments without %- modifier (e.g., Windows)
                        time_label = dt.strftime("%I:%M %p").lstrip("0")

                    is_day_val = bool(is_day_arr[i])
                    tod = "day" if is_day_val else "night"
                    code = int(weather_code_arr[i]) if weather_code_arr is not None else None
                    svg_name = None
                    desc = ""
                    try:
                        if code is not None:
                            svg_name = get_svg_for_code(code, tod)
                            desc = get_desc_for_code(code)
                    except Exception:
                        svg_name = None
                        desc = ""

                    rain_total = float(rain_arr[i]) + float(showers_arr[i])
                    vis_miles = float(visibility_arr[i]) * 0.000621371

                    hourly_item = {
                        "Time": time_label,
                        "svg": svg_name,
                        "description": desc,
                        "Temp": float(temperature[i]),
                        "Feels": float(apparent_temperature[i]),
                        "Humidity": float(relative_humidity[i]),
                        "Cloud cover": float(cloud_cover_arr[i]),
                        "Rainfall": float(rain_total),
                        "Snowfall": float(snowfall_arr[i]),
                        "Precip.": float(precip_prob_arr[i]),
                        "Wind": float(wind_speed_arr[i]),
                        "Gusts": float(wind_gusts_arr[i]),
                        "Visibility": float(vis_miles),
                        "UV": float(uv_index_arr[i]),
                    }
                    hourly_list.append(hourly_item)

                result["hourly"] = hourly_list
            except Exception:
                # If hourly extraction fails, omit hourly key but continue
                pass

            # Emit the result back to the GUI thread
            self.weather_fetched.emit(result)
        except Exception as exc:
            # Convert exceptions to a string message for the GUI to display
            self.fetch_failed.emit(str(exc))
