"""Main window implementation for WeatherApp."""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from typing import Optional

from weatherapp.gui.worker import Worker
from weatherapp.utils.weather_code_mapper import get_svg_for_code, get_desc_for_code


class MainWindow(QWidget):
    """Minimal main window for WeatherApp (Version-0).

    This class sets up the basic UI widgets used to display current weather,
    wires them to a background Worker running in a QThread, and ensures that
    all network I/O happens off the Qt main thread. UI updates are performed
    only in response to signals from the Worker.
    """

    # Expose a signal to request the worker to fetch (queued across threads)
    request_fetch = pyqtSignal()

    def __init__(self) -> None:
        """Construct the window, layout widgets, and start the worker thread.

        The constructor intentionally performs no blocking operations. The
        background worker is moved to a separate QThread and started; fetch
        requests are made by emitting the `request_fetch` signal.
        """
        super().__init__()
        self.setWindowTitle("WeatherApp")

        # Basic widgets: temperature, description, and a manual refresh button
        self.weather_label = QLabel("--")
        self.temp_label = QLabel("--°F")
        self.apparent_label = QLabel("Feels like: --°F")
        self.humidity_label = QLabel("Humidity: --%")
        self.cloud_label = QLabel("Cloud cover: --%")
        self.rain_label = QLabel("Rainfall: -- in")
        self.snow_label = QLabel("Snowfall: -- in")
        self.precip_label = QLabel("Precip: --%")
        self.wind_label = QLabel("Wind: -- mph (Gusts: -- mph)")
        self.visibility_label = QLabel("Visibility: -- mi")
        self.uv_label = QLabel("UV index: --")
        self.refresh_button = QPushButton("Refresh Now")

        # Layout: vertical stack for simplicity and clarity
        layout = QVBoxLayout()
        layout.addWidget(self.weather_label)
        layout.addWidget(self.temp_label)
        layout.addWidget(self.apparent_label)
        layout.addWidget(self.humidity_label)
        layout.addWidget(self.cloud_label)
        layout.addWidget(self.rain_label)
        layout.addWidget(self.snow_label)
        layout.addWidget(self.precip_label)
        layout.addWidget(self.wind_label)
        layout.addWidget(self.visibility_label)
        layout.addWidget(self.uv_label)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        # Worker thread setup: create thread, worker, and connect signals/slots
        self._thread: Optional[QThread] = QThread()
        self._worker = Worker()
        self._worker.moveToThread(self._thread)

        # Connect: request_fetch emits a queued call to worker.fetch
        self.request_fetch.connect(self._worker.fetch)

        # Worker -> GUI signals: update display or show errors
        self._worker.weather_fetched.connect(self.on_weather_fetched)
        self._worker.fetch_failed.connect(self.on_fetch_failed)

        # Start the thread; worker is now able to process fetch requests
        self._thread.start()

        # Connect UI actions to request a fetch when the user clicks the button
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        # Automatic refresh every 10 minutes (600000 ms)
        self._timer = QTimer(self)
        self._timer.setInterval(10 * 60 * 1000)
        self._timer.timeout.connect(self.on_refresh_clicked)
        self._timer.start()

    def closeEvent(self, event) -> None:
        """Handle window close and ensure the worker thread is stopped cleanly.

        We attempt to quit and wait for the thread to finish; any exceptions are
        ignored to avoid crashing during application shutdown.
        """
        try:
            self._thread.quit()
            self._thread.wait()
        except Exception:
            # Swallow errors during shutdown to avoid raising in closeEvent
            pass
        super().closeEvent(event)

    def on_refresh_clicked(self) -> None:
        """Emit a queued fetch request to the Worker.

        Using a signal ensures the call crosses thread boundaries safely and
        avoids invoking worker methods directly from the GUI thread.
        """
        self.request_fetch.emit()

    def on_weather_fetched(self, data: dict) -> None:
        """Update UI widgets with data returned from the Worker.

        The Worker emits a dict containing many current-weather fields. We
        defensively extract the requested fields and update the labels. Any
        unexpected structure triggers a non-fatal warning dialog.
        """
        try:
            # Update weather icon/description
            if "weather" in data:
                self.weather_label.setText(str(data["weather"]))
            elif "svg" in data or "description" in data:
                svg = data.get("svg", "--")
                desc = data.get("description", "--")
                self.weather_label.setText(f"{svg} ({desc})")

            # Temperature and apparent temperature
            if "temperature_2m" in data:
                self.temp_label.setText(f"{int(round(data['temperature_2m']))}°F")
            if "apparent_temperature" in data:
                self.apparent_label.setText(f"Feels like: {int(round(data['apparent_temperature']))}°F")

            # Humidity and cloud cover
            if "relative_humidity_2m" in data:
                self.humidity_label.setText(f"Humidity: {int(round(data['relative_humidity_2m']))}%")
            if "cloud_cover" in data:
                self.cloud_label.setText(f"Cloud cover: {int(round(data['cloud_cover']))}%")

            # Precipitation: rain and snowfall and precip probability
            if "rain" in data:
                self.rain_label.setText(f"Rainfall: {float(data['rain']):.2f} in")
            if "snowfall" in data:
                self.snow_label.setText(f"Snowfall: {float(data['snowfall']):.2f} in")
            if "precipitation_probability" in data:
                self.precip_label.setText(f"Precip: {int(round(data['precipitation_probability']))}%")

            # Wind
            if "wind_speed" in data or "wind_gusts" in data:
                ws = data.get("wind_speed", 0)
                wg = data.get("wind_gusts", 0)
                self.wind_label.setText(f"Wind: {float(ws):.1f} mph (Gusts: {float(wg):.1f} mph)")

            # Visibility and UV index
            if "visibility" in data:
                self.visibility_label.setText(f"Visibility: {float(data['visibility']):.1f} mi")
            if "uv_index" in data:
                self.uv_label.setText(f"UV index: {int(round(data['uv_index']))}")

        except Exception as exc:
            # Defensive: show error but don't crash the application
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        """Show a critical message when the Worker reports a fetch failure.

        Errors are presented in a blocking QMessageBox so the user is clearly
        informed about transient network or API failures.
        """
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
