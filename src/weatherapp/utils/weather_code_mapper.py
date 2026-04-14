"""
Map Open-Meteo weather codes (0–99) to:
- Local SVG filenames (day/night variants)
- Human-readable descriptions

Used by the PyQt6 GUI and CLI output.

Icons live in: ~/Projects/WeatherApp/src/weatherapp/icons/
Downloaded via: utils/download_icons.sh
"""

# ---------------------------
# SVG mapping (day/night)
# ---------------------------
WEATHER_CODE_TO_SVG = {
    0: {"day": "clear-day.svg", "night": "clear-night.svg"},
    1: {"day": "cloudy-day-1.svg", "night": "cloudy-night-1.svg"},
    2: {"day": "cloudy-day-3.svg", "night": "cloudy-night-3.svg"},
    3: {"day": "cloudy.svg", "night": "cloudy.svg"},
    45: {"day": "fog-day.svg", "night": "fog-night.svg"},
    48: {"day": "fog.svg", "night": "fog.svg"},
    51: {"day": "rainy-1-day.svg", "night": "rainy-1-night.svg"},
    53: {"day": "rainy-2-day.svg", "night": "rainy-2-night.svg"},
    55: {"day": "rainy-3-day.svg", "night": "rainy-3-night.svg"},
    56: {"day": "rain-and-sleet-mix.svg", "night": "rain-and-sleet-mix.svg"},
    57: {"day": "rain-and-sleet-mix.svg", "night": "rain-and-sleet-mix.svg"},
    61: {"day": "rainy-1-day.svg", "night": "rainy-1-night.svg"},
    63: {"day": "rainy-2-day.svg", "night": "rainy-2-night.svg"},
    65: {"day": "rainy-3-day.svg", "night": "rainy-3-night.svg"},
    66: {"day": "rain-and-sleet-mix.svg", "night": "rain-and-sleet-mix.svg"},
    67: {"day": "rain-and-sleet-mix.svg", "night": "rain-and-sleet-mix.svg"},
    71: {"day": "snowy-1-day.svg", "night": "snowy-1-night.svg"},
    73: {"day": "snowy-2-day.svg", "night": "snowy-2-night.svg"},
    75: {"day": "snowy-3-day.svg", "night": "snowy-3-night.svg"},
    77: {"day": "snow-and-sleet-mix.svg", "night": "snow-and-sleet-mix.svg"},
    80: {"day": "rainy-1-day.svg", "night": "rainy-1-night.svg"},
    81: {"day": "rainy-2-day.svg", "night": "rainy-2-night.svg"},
    82: {"day": "rainy-3-day.svg", "night": "rainy-3-night.svg"},
    85: {"day": "rain-and-snow-mix.svg", "night": "rain-and-snow-mix.svg"},
    86: {"day": "rain-and-snow-mix.svg", "night": "rain-and-snow-mix.svg"},
    95: {"day": "isolated-thunderstorm-day.svg", "night": "isolated-thunderstorm-night.svg"},
    96: {"day": "scattered-thunderstorm-day.svg", "night": "scattered-thunderstorm-night.svg"},
    99: {"day": "severe-thunderstorm.svg", "night": "severe-thunderstorm.svg"},
    # 0: {"day": "wi-day-sunny.svg", "night": "wi-night-clear.svg"},
    # 1: {"day": "wi-day-sunny.svg", "night": "wi-night-clear.svg"},
    # 2: {"day": "wi-day-cloudy.svg", "night": "wi-night-alt-cloudy.svg"},
    # 3: {"day": "wi-cloudy.svg", "night": "wi-cloudy.svg"},
    # 45: {"day": "wi-day-fog.svg", "night": "wi-night-fog.svg"},
    # 48: {"day": "wi-day-fog.svg", "night": "wi-night-fog.svg"},
    # 51: {"day": "wi-day-sprinkle.svg", "night": "wi-night-sprinkle.svg"},
    # 53: {"day": "wi-day-sprinkle.svg", "night": "wi-night-sprinkle.svg"},
    # 55: {"day": "wi-day-sprinkle.svg", "night": "wi-night-sprinkle.svg"},
    # 56: {"day": "wi-day-sleet.svg", "night": "wi-night-sleet.svg"},
    # 57: {"day": "wi-day-sleet.svg", "night": "wi-night-sleet.svg"},
    # 61: {"day": "wi-day-showers.svg", "night": "wi-night-alt-showers.svg"},
    # 63: {"day": "wi-day-rain.svg", "night": "wi-night-alt-rain.svg"},
    # 65: {"day": "wi-day-rain.svg", "night": "wi-night-alt-rain.svg"},
    # 66: {"day": "wi-day-rain-mix.svg", "night": "wi-night-alt-rain-mix.svg"},
    # 67: {"day": "wi-day-rain-mix.svg", "night": "wi-night-alt-rain-mix.svg"},
    # 71: {"day": "wi-day-snow.svg", "night": "wi-night-alt-snow.svg"},
    # 73: {"day": "wi-day-snow.svg", "night": "wi-night-alt-snow.svg"},
    # 75: {"day": "wi-day-snow-wind.svg", "night": "wi-night-alt-snow-wind.svg"},
    # 77: {"day": "wi-day-snow-wind.svg", "night": "wi-night-alt-snow-wind.svg"},
    # 80: {"day": "wi-day-showers.svg", "night": "wi-night-alt-showers.svg"},
    # 81: {"day": "wi-day-rain.svg", "night": "wi-night-alt-rain.svg"},
    # 82: {"day": "wi-day-rain.svg", "night": "wi-night-alt-rain.svg"},
    # 85: {"day": "wi-day-snow.svg", "night": "wi-night-alt-snow.svg"},
    # 86: {"day": "wi-day-snow-wind.svg", "night": "wi-night-alt-snow-wind.svg"},
    # 95: {"day": "wi-day-thunderstorm.svg", "night": "wi-night-alt-thunderstorm.svg"},
    # 96: {"day": "wi-day-hail.svg", "night": "wi-night-alt-hail.svg"},
    # 99: {"day": "wi-day-sleet-storm.svg", "night": "wi-night-alt-sleet-storm.svg"},
}

UNKNOWN_ICON = {"day": "wi-na.svg", "night": "wi-na.svg"}

# ---------------------------
# Description mapping (single string)
# ---------------------------
WEATHER_CODE_TO_DESC = {
    0: "clear sky",
    1: "mostly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "light fog",
    48: "heavy fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "heavy drizzle",
    56: "light freezing drizzle",
    57: "heavy freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow",
    73: "moderate snow",
    75: "heavy snow",
    77: "grainy snow",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with hail",
    99: "thunderstorm with hail",
}

UNKNOWN_DESC = "--"

# ---------------------------
# Helpers
# ---------------------------
def get_svg_for_code(code: int, time_of_day: str = "day") -> str:
    """Return the SVG filename for a given weather code and time of day."""
    return WEATHER_CODE_TO_SVG.get(code, UNKNOWN_ICON).get(time_of_day, "wi-na.svg")


def get_desc_for_code(code: int) -> str:
    """Return human-readable description for a given weather code."""
    return WEATHER_CODE_TO_DESC.get(code, UNKNOWN_DESC)
