"""Background worker module for WeatherApp GUI.

This module provides the Worker QObject used to execute network I/O in a
separate thread. The module avoids importing the heavy data client at
import time to keep the GUI modules importable for tests and static checks.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# Default coordinates in lieu of user input
# DEFAULT_COORDS = (40.7128, -74.0060)  # New York City
DEFAULT_COORDS = (42.250967869842874, -83.66940204731466) # Ann Arbor

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

    def __init__(self, coords: tuple[float, float] = DEFAULT_COORDS) -> None:
        """Initialize the worker with optional coordinates.

        Args:
            coords: Tuple of (latitude, longitude). Defaults to a fixed location
            used for development and testing.
        """
        super().__init__()
        self.coords = coords

    @pyqtSlot(float, float)
    def set_coords(self, lat: float, lon: float) -> None:
        """Update worker coordinates.

        This slot is intended to be called from the GUI thread via a queued
        signal so the update is synchronized with fetch requests. Invalid
        coordinates are ignored to preserve the previous valid value.
        """
        try:
            latf = float(lat)
            lonf = float(lon)
            # Basic validation of ranges
            if not (-90.0 <= latf <= 90.0 and -180.0 <= lonf <= 180.0):
                return
            self.coords = (latf, lonf)
        except Exception:
            # Ignore invalid inputs and keep existing coordinates
            return

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
            from weatherapp.data.get_weather_data import fetch_weather
            # lightweight helpers for mapping codes
            from weatherapp.utils.weather_code_mapper import get_svg_for_code, get_desc_for_code

            response = fetch_weather(self.coords)

            # Get local timezome from response
            timezone_str = response.Timezone().decode("utf-8")

            result = {}

            try:
                # Get current weather data
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

                # Round wind and gusts to nearest integer per Version-2.2 requirements
                try:
                    wind_speed = int(round(float(current.Variables(9).Value())))
                except Exception:
                    # fallback to previously parsed value
                    try:
                        wind_speed = int(round(float(wind_speed)))
                    except Exception:
                        pass
                try:
                    wind_gusts = int(round(float(current.Variables(10).Value())))
                except Exception:
                    try:
                        wind_gusts = int(round(float(wind_gusts)))
                    except Exception:
                        pass

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

            # Build hourly payload (list of 24 dicts) when available
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

                tz = ZoneInfo(timezone_str)

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

                    # Round wind and gusts to nearest integer for each hourly item
                    try:
                        wind_val = int(round(float(wind_speed_arr[i])))
                    except Exception:
                        try:
                            wind_val = int(round(float(wind_speed_arr[i].item())))
                        except Exception:
                            wind_val = None
                    try:
                        gust_val = int(round(float(wind_gusts_arr[i])))
                    except Exception:
                        try:
                            gust_val = int(round(float(wind_gusts_arr[i].item())))
                        except Exception:
                            gust_val = None

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
                        "Wind": wind_val,
                        "Gusts": gust_val,
                        "Visibility": float(vis_miles),
                        "UV": float(uv_index_arr[i]),
                    }
                    hourly_list.append(hourly_item)

                # Select the next 24 hours beginning with the hour after the current hour
                try:
                    now_ts = int(datetime.now(timezone.utc).timestamp())
                    current_index = int((now_ts - start_ts) // interval)
                    start_index = current_index + 1
                    if start_index < 0:
                        start_index = 0
                    hourly_slice = hourly_list[start_index : start_index + 24]
                    if not hourly_slice:
                        hourly_slice = hourly_list[:24]
                    result["hourly"] = hourly_slice
                except Exception:
                    result["hourly"] = hourly_list[:24]
            except Exception:
                # If hourly extraction fails, omit hourly key but continue
                pass

            # Build daily payload (7 days starting with tomorrow) when available
            try:
                daily = response.Daily()
                # Variables indices correspond to get_weather_data params for daily
                # Many daily fields (sunrise/sunset) are strings; attempt ValuesAsNumpy
                def _maybe_values(var):
                    try:
                        return var.ValuesAsNumpy()
                    except Exception:
                        try:
                            return var.Values()
                        except Exception:
                            return None

                weather_code_arr = _maybe_values(daily.Variables(0))
                sunrise_arr = daily.Variables(1).ValuesInt64AsNumpy()
                sunset_arr = daily.Variables(2).ValuesInt64AsNumpy()
                rain_sum_arr = _maybe_values(daily.Variables(3))
                showers_sum_arr = _maybe_values(daily.Variables(4))
                snowfall_sum_arr = _maybe_values(daily.Variables(5))
                uv_max_arr = _maybe_values(daily.Variables(6))
                temp_max_arr = _maybe_values(daily.Variables(7))
                temp_min_arr = _maybe_values(daily.Variables(8))
                cloud_cover_arr = _maybe_values(daily.Variables(9))
                rel_humidity_arr = _maybe_values(daily.Variables(10))
                precip_prob_arr = _maybe_values(daily.Variables(11))
                visibility_arr = _maybe_values(daily.Variables(12))
                wind_max_arr = _maybe_values(daily.Variables(13))
                gusts_max_arr = _maybe_values(daily.Variables(14))

                # Determine number of days available
                length = None
                for arr in (temp_max_arr, weather_code_arr, sunrise_arr):
                    if arr is not None:
                        try:
                            length = len(arr)
                            break
                        except Exception:
                            continue
                if length is None:
                    raise RuntimeError("Daily arrays not found")

                daily_list = []

                # Helper to parse ISO-ish datetime strings into aware datetimes
                def _parse_iso(dt_str):
                    if dt_str is None:
                        return None
                    if isinstance(dt_str, (int, float)):
                        try:
                            return datetime.fromtimestamp(int(dt_str), tz=timezone.utc).astimezone(ZoneInfo(timezone_str))
                        except Exception:
                            return None
                    try:
                        s = str(dt_str)
                        # Support trailing Z
                        if s.endswith("Z"):
                            s = s[:-1] + "+00:00"
                        return datetime.fromisoformat(s)
                    except Exception:
                        try:
                            # Try parsing date part only
                            return datetime.strptime(s.split("T")[0], "%Y-%m-%d")
                        except Exception:
                            return None

                for i in range(length):
                    # Skip index 0 (today) to start with tomorrow
                    if i == 0:
                        continue
                    try:
                        # Date: prefer sunrise date if available, otherwise construct from index
                        sunrise_val = None
                        try:
                            sunrise_val = sunrise_arr[i]
                        except Exception:
                            pass
                        dt = _parse_iso(sunrise_val) if sunrise_val is not None else None
                        if dt is None:
                            # Fallback to using today's date + i days
                            dt = datetime.now(ZoneInfo(timezone_str)).date() + timedelta(days=i)
                            # normalize to datetime
                            dt = datetime(dt.year, dt.month, dt.day)

                        # Format Date as MM-DD (AbbrevWeekday)
                        try:
                            date_label = dt.strftime("%m-%d (%a)")
                        except Exception:
                            date_label = dt.strftime("%m-%d") + "(%a)"

                        code = None
                        try:
                            code = int(weather_code_arr[i])
                        except Exception:
                            code = None

                        svg_name = None
                        desc = ""
                        try:
                            if code is not None:
                                # Determine day/night for daily icons: use 'day'
                                svg_name = get_svg_for_code(code, "day")
                                desc = get_desc_for_code(code)
                        except Exception:
                            svg_name = None
                            desc = ""

                        rain_total = None
                        try:
                            rain_total = float(rain_sum_arr[i]) + float(showers_sum_arr[i])
                        except Exception:
                            rain_total = None
                        snowfall_total = None
                        try:
                            snowfall_total = float(snowfall_sum_arr[i])
                        except Exception:
                            snowfall_total = None

                        tmax_val = None
                        try:
                            tmax_val = float(temp_max_arr[i])
                        except Exception:
                            tmax_val = None
                        tmin_val = None
                        try:
                            tmin_val = float(temp_min_arr[i])
                        except Exception:
                            tmin_val = None

                        humid_val = None
                        try:
                            humid_val = float(rel_humidity_arr[i])
                        except Exception:
                            humid_val = None

                        cloud_val = None
                        try:
                            cloud_val = float(cloud_cover_arr[i])
                        except Exception:
                            cloud_val = None

                        precip_val = None
                        try:
                            precip_val = float(precip_prob_arr[i])
                        except Exception:
                            precip_val = None

                        wind_val = None
                        try:
                            wind_val = int(round(float(wind_max_arr[i])))
                        except Exception:
                            wind_val = None
                        gust_val = None
                        try:
                            gust_val = int(round(float(gusts_max_arr[i])))
                        except Exception:
                            gust_val = None

                        vis_val = None
                        try:
                            vis_val = float(visibility_arr[i]) * 0.000621371
                        except Exception:
                            vis_val = None

                        uv_val = None
                        try:
                            uv_val = float(uv_max_arr[i])
                        except Exception:
                            uv_val = None

                        sunrise_str = None
                        try:
                            val = sunrise_arr[i]
                            if val is not None:
                                sunrise_dt = datetime.fromtimestamp(int(val), tz=timezone.utc).astimezone(tz)
                                sunrise_str = sunrise_dt.strftime("%-I:%M%p")
                        except Exception:
                            sunrise_str = None

                        sunset_str = None
                        try:
                            val = sunset_arr[i]
                            if val is not None:
                                sunset_dt = datetime.fromtimestamp(int(val), tz=timezone.utc).astimezone(tz)
                                sunset_str = sunset_dt.strftime("%-I:%M%p")
                        except Exception:
                            sunset_str = None

                        daily_item = {
                            "Date": date_label,
                            "svg": svg_name,
                            "description": desc,
                            "Tmax": tmax_val,
                            "Tmin": tmin_val,
                            "Humid_max": humid_val,
                            "Cloud_max": cloud_val,
                            "Rain_tot": rain_total,
                            "Snow_tot": snowfall_total,
                            "Precip_max": precip_val,
                            "Wind_max": wind_val,
                            "Gusts_max": gust_val,
                            "Vis_min": vis_val,
                            "UV_max": uv_val,
                            "Sunrise": sunrise_str,
                            "Sunset": sunset_str,
                        }
                        daily_list.append(daily_item)
                    except Exception:
                        # Skip problematic day but continue
                        continue
                    # Stop after collecting 7 days (tomorrow + 6)
                    if len(daily_list) >= 7:
                        break

                if daily_list:
                    result["daily"] = daily_list
            except Exception:
                # If daily extraction fails, omit daily key but continue
                pass

            # Emit the result back to the GUI thread
            self.weather_fetched.emit(result)
        except Exception as exc:
            # Convert exceptions to a string message for the GUI to display
            self.fetch_failed.emit(str(exc))
