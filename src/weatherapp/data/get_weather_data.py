"""
Backend data provider for the weather GUI application.

This module communicates with the Open-Meteo API, applies caching and retry
logic, and assembles well-structured current, hourly, and daily forecasts to
be consumed by the GUI layer. Location coordinates (lat/lon) are provided by
the GUI layer based on user input.
"""

import logging
from typing import Any, cast

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Configuration constants
CACHE_PATH = ".cache"
CACHE_EXPIRE = 3600  # seconds
RETRIES = 5
BACKOFF_FACTOR = 0.2
URL = "https://api.open-meteo.com/v1/forecast"
FORECAST_DAYS = 10  # Maximum 16 days allowed by API
FORECAST_HOURS = 48
TIMEZONE = "America/New_York"  # Local timezone for displaying times

# Query parameters for the Open-Meteo API request
params = {
    "daily": [
        "weather_code",
        "sunrise",
        "sunset",
        "rain_sum",
        "showers_sum",
        "snowfall_sum",
        "uv_index_max",
        "temperature_2m_mean",
        "apparent_temperature_mean",
        "cloud_cover_mean",
        "relative_humidity_2m_mean",
        "precipitation_probability_mean",
        "visibility_mean",
        "wind_speed_10m_mean",
        "wind_gusts_10m_mean",
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "is_day",
        "precipitation_probability",
        "weather_code",
        "rain",
        "showers",
        "snowfall",
        "cloud_cover",
        "visibility",
        "wind_speed_10m",
        "wind_gusts_10m",
        "uv_index",
    ],
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "is_day",
        "rain",
        "showers",
        "snowfall",
        "weather_code",
        "cloud_cover",
        "wind_speed_10m",
        "wind_gusts_10m",
        "precipitation_probability",
        "visibility",
        "uv_index",
    ],
    "timezone": TIMEZONE,
    "wind_speed_unit": "mph",
    "temperature_unit": "fahrenheit",
    "precipitation_unit": "inch",
    "forecast_days": FORECAST_DAYS,
    "forecast_hours": FORECAST_HOURS,
}


# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("openmeteo_client")


def setup_client() -> openmeteo_requests.Client:
    """
    Create an Open-Meteo API client with caching and retry behavior.

    Returns:
        openmeteo_requests.Client: configured API client.
    """
    try:
        cache_session = requests_cache.CachedSession(
            CACHE_PATH, expire_after=CACHE_EXPIRE
        )
        retry_session = retry(
            cache_session, retries=RETRIES, backoff_factor=BACKOFF_FACTOR
        )
        # Cast to Any to bypass mismatched type stubs between `requests` and the
        # client library; runtime object is a valid session-like object.
        session_to_use = cast(Any, retry_session)
        client = openmeteo_requests.Client(session=session_to_use)
        return client
    except Exception as exc:  # pragma: no cover - network/setup error
        logger.exception("Failed to set up API client: %s", exc)
        raise


def fetch_weather(coords: tuple[float, float]) -> Any:
    """
    Fetch weather data from the Open-Meteo API.

    Args:
        client: Configured API client.
        params: Query parameters for the request.

    Returns:
        The raw response object from the client.
    """
    client = setup_client()

    try:
        # Add location latitude/longitude to params before fetching data
        params["latitude"] = coords[0]
        params["longitude"] = coords[1]

        responses = client.weather_api(URL, params=params)
        if not responses:
            raise RuntimeError("Empty response list from weather_api")
        return responses[0]
    except Exception as exc:
        logger.exception(
            "Error fetching weather data with params: %s; error: %s", params, exc
        )
        raise
