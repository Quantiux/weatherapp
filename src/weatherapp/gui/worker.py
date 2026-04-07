from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from typing import Any

from weatherapp.data.get_weather_data import fetch_weather


class Worker(QObject):
    """Background worker that runs in a QThread and fetches weather data."""

    weather_fetched = pyqtSignal(object)  # emits a dict-like result
    fetch_failed = pyqtSignal(str)  # emits error message

    def __init__(self, coords: tuple[float, float] = (42.250967869842874, -83.66940204731466)) -> None:
        super().__init__()
        self.coords = coords

    @pyqtSlot()
    def fetch(self) -> None:
        """Fetch weather data and emit signals on completion or failure."""
        try:
            response = fetch_weather(self.coords)
            # The GUI consumes only a minimal subset: temperature and description.
            # Use the response object as opaque and extract via attributes used in format.show_weather
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

            self.weather_fetched.emit(result)
        except Exception as exc:
            self.fetch_failed.emit(str(exc))
