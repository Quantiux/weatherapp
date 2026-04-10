"""Main window implementation for WeatherApp.

Version-2.1: display mapping for visibility and UV index values and ensure
hourly description shows the SVG icon immediately followed by the
parenthesized description with no spacing. Only visual/display logic is
changed — worker threads, networking, and data structures are unchanged.
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
    """Main window for WeatherApp with display adjustments for Version-2.1.

    Behavioral logic (threads, signals, data handling) is unchanged.
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
        # Render a smaller SVG icon (~48x48) for Version-2.1 and avoid
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
        self.visibility_label = QLabel("--")
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

        # --- Begin 48-hour forecast area (Version-2.1) ---
        from PyQt6.QtWidgets import QScrollArea, QFrame

        forecast_header = QLabel("48-hr forecast:")
        # Keep header styling minimal and consistent with current app style
        header_font = forecast_header.font()
        header_font.setPointSize(max(9, header_font.pointSize() + 2))
        header_font.setBold(True)
        forecast_header.setFont(header_font)

        # Scrollable area to host the forecast grid (helps with limited vertical space)
        forecast_scroll = QScrollArea()
        forecast_scroll.setWidgetResizable(True)
        forecast_container = QFrame()
        forecast_layout = QVBoxLayout()
        forecast_container.setLayout(forecast_layout)

        # Forecast grid: 13 columns as specified in CURRENT_TASK.md
        forecast_grid = QGridLayout()
        forecast_grid.setVerticalSpacing(6)
        forecast_grid.setHorizontalSpacing(8)

        headers = [
            "Time",
            "Description",
            "Temp",
            "Feels",
            "Humidity",
            "Cloud cover",
            "Rainfall",
            "Snowfall",
            "Precip.",
            "Wind",
            "Gusts",
            "Visibility",
            "UV",
        ]
        for col, text in enumerate(headers):
            h = QLabel(text)
            hf = h.font()
            hf.setPointSize(max(8, hf.pointSize()))
            hf.setBold(True)
            h.setFont(hf)
            h.setAlignment(Qt.AlignmentFlag.AlignCenter)
            forecast_grid.addWidget(h, 0, col)

        # Create placeholders for 48 rows of forecast widgets; store references
        self._forecast_rows = []
        for row in range(1, 49):
            cells = {}
            for col, key in enumerate(headers):
                if key == "Description":
                    # Use a horizontal layout with icon QLabel and text QLabel
                    cell_widget = QWidget()
                    cell_layout = QHBoxLayout()
                    # Remove spacing so the icon and the parentheses touch
                    cell_layout.setContentsMargins(0, 0, 0, 0)
                    cell_layout.setSpacing(0)
                    icon = QLabel()
                    icon.setFixedSize(24, 24)
                    icon.setScaledContents(False)
                    text = QLabel("--")
                    # Left-align text next to the icon with no extra gap
                    text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    cell_layout.addWidget(icon)
                    cell_layout.addWidget(text)
                    cell_widget.setLayout(cell_layout)
                    forecast_grid.addWidget(cell_widget, row, col)
                    cells["Description_icon"] = icon
                    cells["Description_text"] = text
                else:
                    lbl = QLabel("--")
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    forecast_grid.addWidget(lbl, row, col)
                    cells[key] = lbl
            self._forecast_rows.append(cells)

        forecast_layout.addLayout(forecast_grid)
        forecast_scroll.setWidget(forecast_container)

        layout.addWidget(forecast_header)
        layout.addWidget(forecast_scroll)
        self.setLayout(layout)

        # --- End 48-hour forecast area ---

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

        # Request an initial fetch to populate UI
        self.request_fetch.emit()

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

    def _visibility_text(self, vis_val) -> str:
        """Map numeric visibility (miles) to textual categories.

        Rules:
        - "Clear" if visibility is 10 miles or more
        - "Fair" if visibility is 5 miles or more but less than 10 miles
        - "Poor" if visibility is 1 mile or more but less than 5 miles
        - "Zero" otherwise
        """
        try:
            v = float(vis_val)
        except Exception:
            return "--"
        if v >= 10:
            return "Clear"
        if v >= 5:
            return "Fair"
        if v >= 1:
            return "Poor"
        return "Zero"

    def _uv_text(self, uv_val) -> str:
        """Map numeric UV index to textual categories.

        Rules:
        - "Low" if UV Index is 2 or less
        - "Moderate" if UV Index is 3 to 5
        - "High" if UV Index is 6 to 7
        - "Very High" if UV Index is 8 to 10
        - "Extreme" if UV Index is 11 or more
        """
        try:
            u = float(uv_val)
        except Exception:
            return "--"
        if u <= 2:
            return "Low"
        if 3 <= u <= 5:
            return "Moderate"
        if 6 <= u <= 7:
            return "High"
        if 8 <= u <= 10:
            return "Very High"
        if u >= 11:
            return "Extreme"
        return "--"

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

            # Visibility and UV index — map to text categories per CURRENT_TASK.md
            if "visibility" in data:
                self.visibility_label.setText(self._visibility_text(data["visibility"]))
            if "uv_index" in data:
                self.uv_label.setText(self._uv_text(data["uv_index"]))

            # Hourly forecast: update forecast rows if present
            hourly = data.get("hourly")
            if hourly and isinstance(hourly, list):
                for i, item in enumerate(hourly[:48]):
                    cells = self._forecast_rows[i]
                    # Time
                    cells["Time"].setText(item.get("Time", "--"))
                    # Description: load svg into icon QLabel and set text with no
                    # separating space so the icon and parentheses touch visually.
                    svg_name = item.get("svg")
                    if svg_name:
                        try:
                            renderer = QSvgRenderer(str(self._icons_dir / svg_name))
                            size = 24
                            px = QPixmap(size, size)
                            px.fill(Qt.GlobalColor.transparent)
                            p = QPainter(px)
                            renderer.render(p, QRectF(0, 0, float(size), float(size)))
                            p.end()
                            cells["Description_icon"].setPixmap(px)
                        except Exception:
                            cells["Description_icon"].clear()
                    else:
                        cells["Description_icon"].clear()
                    # Description text (parentheses) with no leading space
                    desc_text = item.get("description")
                    if desc_text:
                        cells["Description_text"].setText(f"({desc_text})")
                    else:
                        cells["Description_text"].setText("--")

                    # Numeric fields formatted similar to current view but
                    # Visibility and UV map to textual categories.
                    def _fmt_num(key, fmt):
                        val = item.get(key)
                        if val is None:
                            return "--"
                        try:
                            if isinstance(val, float):
                                return fmt.format(val)
                            return str(val)
                        except Exception:
                            return "--"

                    cells["Temp"].setText(_fmt_num("Temp", "{:.0f}°F"))
                    cells["Feels"].setText(_fmt_num("Feels", "{:.0f}°F"))
                    cells["Humidity"].setText(_fmt_num("Humidity", "{:.0f}%"))
                    cells["Cloud cover"].setText(_fmt_num("Cloud cover", "{:.0f}%"))
                    cells["Rainfall"].setText(_fmt_num("Rainfall", "{:.2f} in"))
                    cells["Snowfall"].setText(_fmt_num("Snowfall", "{:.2f} in"))
                    cells["Precip."].setText(_fmt_num("Precip.", "{:.0f}%"))
                    cells["Wind"].setText(_fmt_num("Wind", "{:.1f} mph"))
                    cells["Gusts"].setText(_fmt_num("Gusts", "{:.1f} mph"))

                    # Visibility -> textual category
                    vis_val = item.get("Visibility")
                    if vis_val is None:
                        cells["Visibility"].setText("--")
                    else:
                        try:
                            cells["Visibility"].setText(self._visibility_text(vis_val))
                        except Exception:
                            cells["Visibility"].setText("--")

                    # UV -> textual category
                    uv_val = item.get("UV")
                    if uv_val is None:
                        cells["UV"].setText("--")
                    else:
                        try:
                            cells["UV"].setText(self._uv_text(uv_val))
                        except Exception:
                            cells["UV"].setText("--")

        except Exception as exc:
            # Defensive: show error but don't crash the application
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        """Show a critical message when the Worker reports a fetch failure.

        Errors are presented in a blocking QMessageBox so the user is clearly
        informed about transient network or API failures.
        """
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
