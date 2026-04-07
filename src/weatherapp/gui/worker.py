"""Background worker module for WeatherApp GUI.

This module provides the Worker QObject used to execute network I/O in a
separate thread. The module avoids importing the heavy data client at
import time to keep the GUI modules importable for tests and static checks.
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Any

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
        attempts to extract a minimal set of fields (temperature, weather
        code, is_day) using the response object's accessor methods. If the
        structured access fails, the raw response is forwarded to the GUI as a
        fallback to preserve information for debugging or display.
        """
        try:
            # Import the data-layer fetcher here to avoid heavy imports at module import time
            from weatherapp.data.get_weather_data import fetch_weather
            response = fetch_weather(self.coords)

            # Try to extract expected fields from the response using the
            # object's accessor methods. The indices used here mirror the
            # structure consumed elsewhere by the project (format.show_weather).
            try:
                current = response.Current()
                temp = float(current.Variables(0).Value())
                weather_code = int(current.Variables(7).Value())
                is_day = bool(current.Variables(3).Value())
                result = {
                    "temperature_2m": temp,
                    "weather_code": weather_code,
                    "is_day": is_day,
                }
            except Exception:
                # Fallback: pass the whole response if structured access fails
                result = {"response": response}

            # Emit the result back to the GUI thread
            self.weather_fetched.emit(result)
        except Exception as exc:
            # Convert exceptions to a string message for the GUI to display
            self.fetch_failed.emit(str(exc))
