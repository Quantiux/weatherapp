"""Main window implementation for WeatherApp.

Version-1.3: typography and alignment improvements only. Changes are
restricted to visual presentation (icon size/alignment, fonts, spacing)
and do not affect worker threads, networking, or data structures.
"""

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
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QFont
from PyQt6.QtSvg import QSvgRenderer
from typing import Optional

from weatherapp.gui.worker import Worker
from weatherapp.utils.weather_code_mapper import get_svg_for_code, get_desc_for_code


class MainWindow(QWidget):
    """Main window for WeatherApp with minor UI typography tweaks.

    All behavioral logic (threads, signals, data handling) is unchanged.
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
        # Render a smaller SVG icon (~48x48) for Version-1.3 and avoid
        # stretching by disabling scaledContents and controlling rendering
        # in _load_svg_pixmap.
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setScaledContents(False)
        self.weather_label = QLabel("--")
        # Make the description visually prominent compared to the
        # data-grid labels while preserving the parentheses per the
        # version requirement.
        desc_font = self.weather_label.font()
        desc_font.setPointSize(max(11, desc_font.pointSize() + 4))
        desc_font.setBold(True)
        self.weather_label.setFont(desc_font)

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

        # Top row: icon then weather description. Keep a small spacing
        # between the icon and the description and align them vertically.
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(self.icon_label)
        top_row.addWidget(self.weather_label)

        # Layout: top row followed by a compact two-column grid of fields
        layout = QVBoxLayout()
        # Improve overall spacing and margins for clarity
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addLayout(top_row)

        grid = QGridLayout()
        # Increase spacing between rows/columns so entries are easier to read
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(12)
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
            # Slightly larger font for readability
            name_font = name_label.font()
            name_font.setPointSize(max(9, name_font.pointSize() + 1))
            name_label.setFont(name_font)
            name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Increase value label font size as well and keep right alignment
            val_font = widget.font()
            val_font.setPointSize(max(9, val_font.pointSize() + 1))
            widget.setFont(val_font)
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

        Returns a 48x48 QPixmap on success or None on failure. The SVG is
        rendered into a square target while preserving aspect ratio to avoid
        distortion.
        """
        if not svg_filename:
            return None
        icon_path = self._icons_dir / svg_filename
        if not icon_path.exists():
            return None
        try:
            renderer = QSvgRenderer(str(icon_path))
            size = 48
            pixmap = QPixmap(size, size)
            # Create a transparent pixmap and render the SVG into a centered
            # rectangle so aspect ratio is preserved and the icon is not
            # distorted.
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            # Target rect covers the full pixmap; QSvgRenderer preserves
            # aspect ratio when rendering into a QRectF if the viewBox is set
            renderer.render(painter, QRectF(0, 0, float(size), float(size)))
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
