"""Backend data formatter for the WeatherApp CLI utilities.

This module fetches current, hourly, and daily forecasts from the shared data
layer, normalizes selected values for terminal display, maps weather codes to
human-readable labels, and prints formatted summaries.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import pandas as pd

from weatherapp.data.get_weather_data import fetch_weather
from weatherapp.utils.weather_code_mapper import get_desc_for_code, get_svg_for_code

VIS_MILES = 0.000621371

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("openmeteo_client")

ColumnFormatter = Callable[[Any], str]
COLUMN_FORMATTERS: dict[str, ColumnFormatter] = {
    "Temp": lambda value: f"{int(round(float(value)))}°F",
    "Feels": lambda value: f"{int(round(float(value)))}°F",
    "T(max)": lambda value: f"{int(round(float(value)))}°F",
    "T(min)": lambda value: f"{int(round(float(value)))}°F",
    "Rainfall": lambda value: f"{float(value):.1f}in",
    "Snowfall": lambda value: f"{float(value):.1f}in",
    "Humidity": lambda value: f"{float(value):.0f}%",
    "Precip.": lambda value: f"{float(value):.0f}%",
    "Cloud cover": lambda value: f"{float(value):.0f}%",
    "Wind": lambda value: f"{int(round(float(value)))}mph",
    "Gusts": lambda value: f"{int(round(float(value)))}mph",
    "Visibility": lambda value: f"{int(round(float(value)))}mi",
    "UV": lambda value: f"{float(value):.1f}",
}


def map_code_to_label(code: int, day_or_night: str) -> str:
    """Return the mapped SVG filename and description for a weather code.

    Args:
        code: Open-Meteo weather code.
        day_or_night: Either ``"day"`` or ``"night"`` for icon selection.

    Returns:
        A string in the form ``"icon.svg (description)"``.
    """
    try:
        svg_name = get_svg_for_code(code, day_or_night)
        description = get_desc_for_code(code)
        return f"{svg_name} ({description})"
    except Exception:
        logger.exception("Failed to map weather_code %s", code)
        return "wi-na.svg (Unknown)"


def _format_display_value(value: Any, format_key: str) -> str:
    """Format a single display value using a named formatter.

    Args:
        value: Raw value extracted from the weather response.
        format_key: Key selecting a formatting rule from ``COLUMN_FORMATTERS``.

    Returns:
        A terminal-friendly string representation.
    """
    try:
        if pd.isna(value):
            return "NaN"
    except Exception:
        return str(value)

    formatter = COLUMN_FORMATTERS.get(format_key)
    if formatter is None:
        return str(value)

    try:
        return formatter(value)
    except Exception:
        return "NaN"



def format_columns(df: pd.DataFrame, col_map: dict[str, str]) -> None:
    """Format DataFrame columns in place for terminal display.

    Args:
        df: DataFrame whose columns should be transformed.
        col_map: Mapping of column name to formatter key.

    Returns:
        None. The input DataFrame is mutated in place.
    """
    for column_name, format_key in col_map.items():
        if column_name in df.columns:
            df[column_name] = df[column_name].map(
                lambda value, current_key=format_key: _format_display_value(
                    value,
                    current_key,
                ),
            )



def parse_current(response: Any) -> None:
    """Extract and print current weather values from an API response.

    Args:
        response: Weather response object returned by ``fetch_weather``.

    Returns:
        None. The formatted current weather summary is printed to stdout.
    """
    try:
        current = response.Current()

        rain_value = float(current.Variables(4).Value())
        showers_value = float(current.Variables(5).Value())
        combined_rain = rain_value + showers_value

        weather_code = current.Variables(7).Value()
        is_day = current.Variables(3).Value()
        day_or_night = "day" if is_day else "night"
        weather_desc = map_code_to_label(weather_code, day_or_night)

        visibility_miles = float(current.Variables(12).Value()) * VIS_MILES

        current_data = {
            "weather": weather_desc,
            "temperature_2m": float(current.Variables(0).Value()),
            "relative_humidity_2m": float(current.Variables(1).Value()),
            "apparent_temperature": float(current.Variables(2).Value()),
            "is_day": bool(current.Variables(3).Value()),
            "rain": combined_rain,
            "snowfall": float(current.Variables(6).Value()),
            "cloud_cover": float(current.Variables(8).Value()),
            "wind_speed": float(current.Variables(9).Value()),
            "wind_gusts": float(current.Variables(10).Value()),
            "precipitation_probability": float(current.Variables(11).Value()),
            "visibility": visibility_miles,
            "uv_index": float(current.Variables(13).Value()),
        }

        print(f"Condition: {current_data['weather']}")
        print(
            "Temp (Feels): "
            f"{current_data['temperature_2m']:.0f}°F "
            f"({current_data['apparent_temperature']:.0f}°F)",
        )
        print(f"Rain Prob.: {current_data['precipitation_probability']:.0f}%")
        print(f"Rainfall: {current_data['rain']:.1f}in")
        print(f"Snowfall: {current_data['snowfall']:.1f}in")
        print(f"Humidity: {current_data['relative_humidity_2m']:.0f}%")
        print(f"Cloud cover: {current_data['cloud_cover']:.0f}%")
        print(
            f"Wind (Gusts): {current_data['wind_speed']:.0f}mph "
            f"({current_data['wind_gusts']:.0f}mph)",
        )
        print(f"Visibility: {current_data['visibility']:.0f}mi")
        print(f"UV Index: {current_data['uv_index']:.0f}")
    except Exception as exc:
        logger.exception("Failed to display current weather: %s", exc)
        raise



def parse_hourly(response: Any) -> None:
    """Extract and print the hourly weather forecast.

    Args:
        response: Weather response object returned by ``fetch_weather``.

    Returns:
        None. The formatted hourly forecast table is printed to stdout.
    """
    try:
        hourly = response.Hourly()
        temperature = hourly.Variables(0).ValuesAsNumpy()
        relative_humidity = hourly.Variables(1).ValuesAsNumpy()
        apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
        is_day = hourly.Variables(3).ValuesAsNumpy()
        precip_probability = hourly.Variables(4).ValuesAsNumpy()
        weather_code = hourly.Variables(5).ValuesAsNumpy()
        rain = hourly.Variables(6).ValuesAsNumpy()
        showers = hourly.Variables(7).ValuesAsNumpy()
        snowfall = hourly.Variables(8).ValuesAsNumpy()
        cloud_cover = hourly.Variables(9).ValuesAsNumpy()
        visibility = hourly.Variables(10).ValuesAsNumpy()
        wind_speed = hourly.Variables(11).ValuesAsNumpy()
        wind_gusts = hourly.Variables(12).ValuesAsNumpy()
        uv_index = hourly.Variables(13).ValuesAsNumpy()

        rain_total = rain + showers

        timezone_name = response.Timezone().decode("utf-8")
        hours = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(
                timezone_name,
            ),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(
                timezone_name,
            ),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
        hours = hours.strftime("%-I:%M %p")

        day_or_night = ["day" if is_day_value else "night" for is_day_value in is_day]
        weather_desc = [
            map_code_to_label(code, period)
            for code, period in zip(weather_code, day_or_night, strict=False)
        ]

        visibility = visibility * VIS_MILES

        hourly_df = pd.DataFrame(
            {
                "Time": hours,
                "Description": weather_desc,
                "Temp": temperature,
                "Feels": apparent_temperature,
                "Humidity": relative_humidity,
                "Cloud cover": cloud_cover,
                "Rainfall": rain_total,
                "Snowfall": snowfall,
                "Precip.": precip_probability,
                "Wind": wind_speed,
                "Gusts": wind_gusts,
                "Visibility": visibility,
                "UV": uv_index,
            },
        )

        col_map = {
            "Temp": "Temp",
            "Feels": "Feels",
            "Humidity": "Humidity",
            "Cloud cover": "Cloud cover",
            "Rainfall": "Rainfall",
            "Snowfall": "Snowfall",
            "Precip.": "Precip.",
            "Wind": "Wind",
            "Gusts": "Gusts",
            "Visibility": "Visibility",
        }
        format_columns(hourly_df, col_map)

        print("\n48-hour forecast:\n" + hourly_df.to_string(index=False))
    except Exception as exc:
        logger.exception("Failed to display hourly weather forecast: %s", exc)
        raise



def parse_daily(response: Any) -> None:
    """Extract and print the daily weather forecast.

    Args:
        response: Weather response object returned by ``fetch_weather``.

    Returns:
        None. The formatted daily forecast table is printed to stdout.
    """
    try:
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_sunrise = daily.Variables(1).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(2).ValuesInt64AsNumpy()
        daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
        daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
        daily_rain_total = daily_rain_sum + daily_showers_sum
        daily_snowfall_sum = daily.Variables(5).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(6).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(7).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(8).ValuesAsNumpy()
        daily_cloud_cover_max = daily.Variables(9).ValuesAsNumpy()
        daily_relative_humidity_2m_max = daily.Variables(10).ValuesAsNumpy()
        daily_precipitation_probability_max = daily.Variables(11).ValuesAsNumpy()
        daily_visibility_min = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(14).ValuesAsNumpy()

        daily_rain_total_in = daily_rain_total / 25.4
        daily_snow_total_in = daily_snowfall_sum / 2.54
        daily_visibility_min = daily_visibility_min * VIS_MILES

        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        )
        dates = dates.strftime("%m-%d (%a)")

        timezone_name = response.Timezone().decode("utf-8")
        daily_sunrise_local = (
            pd.to_datetime(daily_sunrise, unit="s", utc=True)
            .tz_convert(timezone_name)
            .strftime("%-I:%M %p")
        )
        daily_sunset_local = (
            pd.to_datetime(daily_sunset, unit="s", utc=True)
            .tz_convert(timezone_name)
            .strftime("%-I:%M %p")
        )

        weather_desc = [map_code_to_label(code, "day") for code in daily_weather_code]

        daily_df = pd.DataFrame(
            {
                "Date": dates,
                "Description": weather_desc,
                "Temp(max)": daily_temperature_2m_max,
                "Temp(min)": daily_temperature_2m_min,
                "Humidity": daily_relative_humidity_2m_max,
                "Cloud cover": daily_cloud_cover_max,
                "Rainfall": daily_rain_total_in,
                "Snowfall": daily_snow_total_in,
                "Precip.": daily_precipitation_probability_max,
                "Wind": daily_wind_speed_10m_max,
                "Gusts": daily_wind_gusts_10m_max,
                "Visibility": daily_visibility_min,
                "UV": daily_uv_index_max,
                "Sunrise": daily_sunrise_local,
                "Sunset": daily_sunset_local,
            },
        )

        col_map = {
            "T(max)": "Temp(max)",
            "T(min)": "Temp(min)",
            "Humidity": "Humidity",
            "Cloud cover": "Cloud cover",
            "Rainfall": "Rainfall",
            "Snowfall": "Snowfall",
            "Precip.": "Precip.",
            "Wind": "Wind",
            "Gusts": "Gusts",
            "Visibility": "Visibility",
            "UV": "UV",
        }
        format_columns(daily_df, col_map)

        print("\n10-day forecast:\n" + daily_df.to_string(index=False))
    except Exception as exc:
        logger.exception("Failed to process daily weather from response: %s", exc)
        raise



def main() -> None:
    """Fetch weather data and print current, hourly, and daily summaries."""
    latitude = 42.250967869842874
    longitude = -83.66940204731466
    coords = (latitude, longitude)
    try:
        response = fetch_weather(coords)
        parse_current(response)
        parse_hourly(response)
        parse_daily(response)
    except Exception:
        logger.exception("Main execution failed")


if __name__ == "__main__":
    main()
