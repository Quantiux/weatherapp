"""
Backend data formatter for the weather GUI application.

This module collects current, hourly, and daily forecasts from the data layer,
normalizes units, formats values, maps weather codes to human-readable labels and
icons, and feeds the processed output to the GUI layer. Location coordinates
(lat/lon) are provided by the GUI layer based on user input.
"""

import logging
from typing import Any, Dict

import pandas as pd
from weatherapp.data.get_weather_data import fetch_weather
from weatherapp.utils.weather_code_mapper import get_desc_for_code, get_svg_for_code

# Set constants
TIMEZONE = "America/New_York"  # Local timezone for displaying times
VIS_MILES = 0.000621371  # meters to miles conversion factor (for visibility parameter)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("openmeteo_client")


def map_code_to_label(code: int, day_or_night: str) -> str:
    """
    Return a combined string of the form: 'icon.svg (Description)' using the SVG
    mapping and Open-Meteo's built-in code meanings.
    """
    try:
        # map svg and description to weather code
        svg = get_svg_for_code(code, day_or_night)
        desc = get_desc_for_code(code)

        return f"{svg} ({desc})"
    except Exception:
        logger.exception("Failed to map weather_code %s", code)
        return "wi-na.svg (Unknown)"


def format_columns(df: pd.DataFrame, col_map: Dict[str, str]) -> None:
    """
    Format DataFrame columns in place.

    col_map maps column name -> formatting key.
    """

    def _format_value(val: Any, var: str) -> str:
        """Format data for display, handling NaN values."""
        try:
            if pd.isna(val):
                return "NaN"
        except Exception:
            return str(val)

        try:
            if var in {"Temp", "Feels"}:
                return f"{int(round(float(val)))}°F"
            if var in {"Rainfall", "Snowfall"}:
                return f"{float(val):.1f}in"
            if var in {"Humidity", "Precip.", "Cloud cover"}:
                return f"{float(val):.0f}%"
            if var in {"Wind", "Gusts"}:
                return f"{int(round(float(val)))}mph"
            if var == "Visibility":
                return f"{int(round(float(val)))}mi"
            if var == "UV":
                return f"{float(val):.1f}"
            return str(val)
        except Exception:
            return "NaN"

    for col, var in col_map.items():
        if col in df.columns:
            df[col] = df[col].map(lambda v: _format_value(v, var))


def parse_current(response: Any) -> None:
    """
    Extract and display current weather variables from the API response.

    Args:
        response: Response object from fetch_weather.
    """
    try:
        current = response.Current()

        # Variables() indices correspond to requested 'current' list in params.
        # Combine current rain and showers into a single `rain` value.
        rain_val = float(current.Variables(4).Value())
        showers_val = float(current.Variables(5).Value())
        combined_rain = rain_val + showers_val

        # Map current weather code to icon/description
        weather_code = current.Variables(7).Value()
        is_day = current.Variables(3).Value()
        day_or_night = "day" if is_day else "night"
        weather_desc = map_code_to_label(weather_code, day_or_night)

        # Scale visibility from meters to miles
        visibility_miles = float(current.Variables(12).Value()) * VIS_MILES

        # The order of variables must match the requested 'current' list.
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
            f"Temp (Feels): {current_data['temperature_2m']:.0f}°F ({current_data['apparent_temperature']:.0f}°F)"
        )
        print(f"Rain Prob.: {current_data['precipitation_probability']:.0f}%")
        print(f"Rainfall: {current_data['rain']:.1f}in")
        print(f"Snowfall: {current_data['snowfall']:.1f}in")
        print(f"Humidity: {current_data['relative_humidity_2m']:.0f}%")
        print(f"Cloud cover: {current_data['cloud_cover']:.0f}%")
        print(
            f"Wind (Gusts): {current_data['wind_speed']:.0f}mph ({current_data['wind_gusts']:.0f}mph)"
        )
        print(f"Visibility: {current_data['visibility']:.0f}mi")
        print(f"UV Index: {current_data['uv_index']:.0f}")
    except Exception as exc:
        logger.exception("Failed to display current weather: %s", exc)
        raise


def parse_hourly(response: Any) -> None:
    """
    Extract and display next 48 hours of hourly weather variables from the API response.

    Args:
        response: Response object from fetch_weather.
    """
    try:
        hourly = response.Hourly()
        # Variables() indices correspond to requested 'hourly' list in params.
        temperature = hourly.Variables(0).ValuesAsNumpy()
        relative_humidity = hourly.Variables(1).ValuesAsNumpy()
        apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
        is_day = hourly.Variables(3).ValuesAsNumpy()
        precip_prob = hourly.Variables(4).ValuesAsNumpy()
        weather_code = hourly.Variables(5).ValuesAsNumpy()
        rain = hourly.Variables(6).ValuesAsNumpy()
        showers = hourly.Variables(7).ValuesAsNumpy()
        snowfall = hourly.Variables(8).ValuesAsNumpy()
        cloud_cover = hourly.Variables(9).ValuesAsNumpy()
        visibility = hourly.Variables(10).ValuesAsNumpy()
        wind_speed = hourly.Variables(11).ValuesAsNumpy()
        wind_gusts = hourly.Variables(12).ValuesAsNumpy()
        uv_index = hourly.Variables(13).ValuesAsNumpy()

        # Combine rain & showers for a single rain column
        rain_total = rain + showers

        # Build time range for the hourly data and format as "H:MM AM/PM"
        hours = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert(
                TIMEZONE
            ),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert(
                TIMEZONE
            ),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
        hours = hours.strftime("%-I:%M %p")

        # Map current weather code to icon/description
        day_or_night = ["day" if is_day_val else "night" for is_day_val in is_day]
        weather_desc = [
            map_code_to_label(c, dn) for c, dn in zip(weather_code, day_or_night)
        ]

        # Scale visibility from meters to miles
        visibility = visibility * VIS_MILES

        # Build DataFrame
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
                "Precip.": precip_prob,
                "Wind": wind_speed,
                "Gusts": wind_gusts,
                "Visibility": visibility,
                "UV": uv_index,
            }
        )

        # Format data for display
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

        # Print next 48 hours of hourly forecast
        print("\n48-hour forecast:\n" + hourly_df.to_string(index=False))

    except Exception as exc:
        logger.exception("Failed to display hourly weather forecast: %s", exc)
        raise


def parse_daily(response: Any) -> None:
    """
    Extract and display next 10 days of daily weather variables from the API response.

    Args:
        response: Response object from fetch_weather.
    """
    try:
        daily = response.Daily()
        # Variables() indices correspond to requested 'daily' list in params.
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_sunrise = daily.Variables(1).ValuesInt64AsNumpy()
        daily_sunset = daily.Variables(2).ValuesInt64AsNumpy()
        daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
        daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
        # Combine rain_sum and showers_sum into a single column `rain_total`.
        daily_rain_total = daily_rain_sum + daily_showers_sum
        daily_snowfall_sum = daily.Variables(5).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(6).ValuesAsNumpy()
        daily_temperature_2m_mean = daily.Variables(7).ValuesAsNumpy()
        daily_apparent_temperature_2m_mean = daily.Variables(8).ValuesAsNumpy()
        daily_cloud_cover_mean = daily.Variables(9).ValuesAsNumpy()
        daily_relative_humidity_2m_mean = daily.Variables(10).ValuesAsNumpy()
        daily_precipitation_probability_mean = daily.Variables(11).ValuesAsNumpy()
        daily_visibility_mean = daily.Variables(12).ValuesAsNumpy()
        daily_wind_speed_10m_mean = daily.Variables(13).ValuesAsNumpy()
        daily_wind_gusts_10m_mean = daily.Variables(14).ValuesAsNumpy()

        # Convert precipitation units to inches:
        daily_rain_total_in = daily_rain_total / 25.4  # 1 inch = 25.4 mm
        daily_snow_total_in = daily_snowfall_sum / 2.54  # 1 inch = 2.54 cm

        # Scale visibility from meters to miles
        daily_visibility_mean = daily_visibility_mean * VIS_MILES

        # Build date range for the daily data and format as "MM-DD (Ddd)"
        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left",
        )
        dates = dates.strftime("%m-%d (%a)")

        # Format sunrise/sunset (epoch seconds) as local standard time, e.g. "7:15 AM"
        daily_sunrise_local = (
            pd.to_datetime(daily_sunrise, unit="s", utc=True)
            .tz_convert(TIMEZONE)
            .strftime("%-I:%M %p")
        )
        daily_sunset_local = (
            pd.to_datetime(daily_sunset, unit="s", utc=True)
            .tz_convert(TIMEZONE)
            .strftime("%-I:%M %p")
        )

        # Map current weather code to icon/description
        weather_desc = [map_code_to_label(c, "day") for c in daily_weather_code]

        # Build DataFrame
        daily_df = pd.DataFrame(
            {
                "Date": dates,
                "Description": weather_desc,
                "Temp": daily_temperature_2m_mean,
                "Feels": daily_apparent_temperature_2m_mean,
                "Humidity": daily_relative_humidity_2m_mean,
                "Cloud cover": daily_cloud_cover_mean,
                "Rainfall": daily_rain_total_in,
                "Snowfall": daily_snow_total_in,
                "Precip.": daily_precipitation_probability_mean,
                "Wind": daily_wind_speed_10m_mean,
                "Gusts": daily_wind_gusts_10m_mean,
                "Visibility": daily_visibility_mean,
                "UV": daily_uv_index_max,
                "Sunrise": daily_sunrise_local,
                "Sunset": daily_sunset_local,
            }
        )

        # Format data for display
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
            "UV": "UV",
        }
        format_columns(daily_df, col_map)

        # Print next 10 days of daily forecast
        print("\n10-day forecast:\n" + daily_df.to_string(index=False))
    except Exception as exc:
        logger.exception("Failed to process daily weather from response: %s", exc)
        raise


def main() -> None:
    """
    Main entry point: fetch weather, print current summary, and hourly + daily Forecast.
    """
    LATITUDE = 42.250967869842874
    LONGITUDE = -83.66940204731466
    coords = (LATITUDE, LONGITUDE)
    try:
        response = fetch_weather(coords)
        parse_current(response)
        parse_hourly(response)
        parse_daily(response)
    except Exception:
        logger.exception("Main execution failed")


if __name__ == "__main__":
    main()
