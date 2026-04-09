"""Main window implementation for WeatherApp."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from typing import Optional

from weatherapp.gui.worker import Worker
from weatherapp.utils.weather_code_mapper import get_svg_for_code, get_desc_for_code


class MainWindow(QWidget):
    """Minimal main window for WeatherApp (Version-0/1.1).

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

        # Compute icons directory: src/weatherapp/icons
        self._icons_dir = Path(__file__).resolve().parent.parent / "icons"

        # Basic widgets: icon, description, temperature, and a manual refresh button
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setScaledContents(False)
        self.weather_label = QLabel("--")
        self.temp_label = QLabel("--°F")
        self.feels_label = QLabel("--°F")
        self.humidity_label = QLabel("--%")
        self.cloud_label = QLabel("--%")
        self.rain_label = QLabel("-- in")
        self.snow_label = QLabel("-- in")
        self.precip_label = QLabel("--%")
        self.wind_label = QLabel("-- mph")
        self.gusts_label = QLabel("-- mph")
        self.visibility_label = QLabel("-- mi")
        self.uv_label = QLabel("--")
        self.refresh_button = QPushButton("Refresh Now")

        # Top row: icon then weather description
        top_row = QHBoxLayout()
        top_row.addWidget(self.icon_label)
        top_row.addWidget(self.weather_label)

        # Layout: top row followed by a compact two-column grid of fields
        layout = QVBoxLayout()
        layout.addLayout(top_row)

        grid = QGridLayout()
        # Column 0: field name labels (static); Column 1: value labels (dynamic)
        field_names = [
            ("Temperature:", self.temp_label),
            ("Feels like:", self.feels_label),
            ("Humidity:", self.humidity_label),
            ("Cloud cover:", self.cloud_label),
            ("Rainfall:", self.rain_label),
            ("Snowfall:", self.snow_label),
            ("Precip:", self.precip_label),
            ("Wind:", self.wind_label),
            ("Gusts:", self.gusts_label),
            ("Visibility:", self.visibility_label),
            ("UV index:", self.uv_label),
        ]
        for row, (name, widget) in enumerate(field_names):
            name_label = QLabel(name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            grid.addWidget(name_label, row, 0)
            grid.addWidget(widget, row, 1)

        layout.addLayout(grid)
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

    def _load_svg_pixmap(self, svg_filename: str) -> Optional[QPixmap]:
        """Load an SVG file from the icons directory and render it to a QPixmap.

        Returns a 64x64 QPixmap on success or None on failure.
        """
        if not svg_filename:
            return None
        icon_path = self._icons_dir / svg_filename
        if not icon_path.exists():
            return None
        try:
            renderer = QSvgRenderer(str(icon_path))
            pixmap = QPixmap(64, 64)
            # Create a transparent pixmap and render the SVG into it
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return pixmap
        except Exception:
            return None

    def on_weather_fetched(self, data: dict) -> None:
        """Update UI widgets with data returned from the Worker.

        The Worker emits a dict containing many current-weather fields. We
        defensively extract the requested fields and update the labels. Any
        unexpected structure triggers a non-fatal warning dialog.
        """
        try:
            # Icon and description: prefer a rendered icon when "svg" is present
            svg = data.get("svg")
            desc = data.get("description") or data.get("weather")
            if svg:
                pixmap = self._load_svg_pixmap(svg)
                if pixmap:
                    self.icon_label.setPixmap(pixmap)
                else:
                    self.icon_label.clear()
            else:
                self.icon_label.clear()

            # Description text — keep parentheses as in Version-1
            if desc:
                self.weather_label.setText(f"({desc})")
            elif "weather" in data:
                self.weather_label.setText(str(data["weather"]))
            else:
                self.weather_label.setText("--")

            # Temperature and apparent temperature
            if "temperature_2m" in data:
                self.temp_label.setText(f"{int(round(data['temperature_2m']))}°F")
            if "apparent_temperature" in data:
                self.feels_label.setText(f"{int(round(data['apparent_temperature']))}°F")

            # Humidity and cloud cover
            if "relative_humidity_2m" in data:
                self.humidity_label.setText(f"{int(round(data['relative_humidity_2m']))}%")
            if "cloud_cover" in data:
                self.cloud_label.setText(f"{int(round(data['cloud_cover']))}%")

            # Precipitation: rain and snowfall and precip probability
            if "rain" in data:
                self.rain_label.setText(f"{float(data['rain']):.2f} in")
            if "snowfall" in data:
                self.snow_label.setText(f"{float(data['snowfall']):.2f} in")
            if "precipitation_probability" in data:
                self.precip_label.setText(f"{int(round(data['precipitation_probability']))}%")

            # Wind and Gusts
            if "wind_speed" in data:
                self.wind_label.setText(f"{float(data['wind_speed']):.1f} mph")
            if "wind_gusts" in data:
                self.gusts_label.setText(f"{float(data['wind_gusts']):.1f} mph")

            # Visibility and UV index
            if "visibility" in data:
                self.visibility_label.setText(f"{float(data['visibility']):.1f} mi")
            if "uv_index" in data:
                self.uv_label.setText(f"{int(round(data['uv_index']))}")

        except Exception as exc:
            # Defensive: show error but don't crash the application
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        """Show a critical message when the Worker reports a fetch failure.

        Errors are presented in a blocking QMessageBox so the user is clearly
        informed about transient network or API failures.
        """
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
