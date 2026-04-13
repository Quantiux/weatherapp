"""Main window implementation for WeatherApp.

Version-2.2: display mapping for visibility and UV index values and show the
next 24-hour hourly forecast beginning with the hour after the current hour.
Wind and gust values are displayed rounded to the nearest integer.
Only visual/display logic is changed — worker threads, networking, and data
structures are unchanged.
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
    QTabWidget,
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt, QRectF
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from typing import Optional
from datetime import datetime

from weatherapp.gui.worker import Worker

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
        # Render a large SVG icon (~128x128) for Version-4.1 current weather description
        self.icon_label.setFixedSize(128, 128)
        self.icon_label.setScaledContents(False)
        self.weather_label = QLabel("--")
        # Make the description visually prominent compared to the
        # data-grid labels while preserving the parentheses per the
        # version requirement.
        desc_font = self.weather_label.font()
        desc_font.setPointSize(max(11, desc_font.pointSize() + 8))
        desc_font.setBold(True)
        self.weather_label.setFont(desc_font)

        self.temp_label = QLabel("--°F")
        self.feels_label = QLabel("--°F")
        # Combined label for Temperature|Feels (Version-4.2)
        self.temp_feels_label = QLabel("--°F|--°F")
        self.humidity_label = QLabel("--%")
        self.cloud_label = QLabel("--%")
        self.rain_label = QLabel("-- in")
        self.snow_label = QLabel("-- in")
        self.precip_label = QLabel("--%")
        self.wind_label = QLabel("--mph")
        self.gusts_label = QLabel("--mph")
        # Combined label for Wind|Gusts (Version-4.2)
        self.wind_gusts_label = QLabel("--mph|--mph")
        self.visibility_label = QLabel("--")
        self.uv_label = QLabel("--")
        self.refresh_button = QPushButton("Refresh Now")

        # Time row: current time and today's date (placed above icon + description)
        # Left-justified and styled to match the data value font size.
        time_row = QHBoxLayout()
        time_row.setContentsMargins(0, 10, 0, 0)
        time_row.setSpacing(0)
        time_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.time_label = QLabel("--")
        # Use the data-value font as the baseline so the time/date matches the
        # same point size as the grid values below.
        time_font = self.temp_feels_label.font()
        time_font.setPointSize(max(9, time_font.pointSize() + 2))
        self.time_label.setFont(time_font)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        time_row.addWidget(self.time_label)

        # Top row: icon then weather description. Keep a small spacing
        # between the icon and the description and align them vertically.
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(self.icon_label)
        top_row.addWidget(self.weather_label)

        # Layout: we'll place existing UI sections into tabs (NOW, HOURLY, 7-DAY)
        main_layout = QVBoxLayout()
        # Improve overall spacing and margins for clarity
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Prepare the information grid used in the NOW tab
        grid = QGridLayout()
        # Increase spacing between rows/columns so entries are easier to read
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(12)
        # Column 0: field name labels (static); Column 1: value labels (dynamic)
        field_names = [
            ("Temperature | Feels like:", self.temp_feels_label),
            ("Humidity:", self.humidity_label),
            ("Cloud cover:", self.cloud_label),
            ("Rainfall:", self.rain_label),
            ("Snowfall:", self.snow_label),
            ("Precip:", self.precip_label),
            ("Wind | Gusts:", self.wind_gusts_label),
            ("Visibility:", self.visibility_label),
            ("UV index:", self.uv_label),
        ]
        for row, (name, widget) in enumerate(field_names):
            name_label = QLabel(name)
            # Slightly larger font for readability
            name_font = name_label.font()
            name_font.setPointSize(max(9, name_font.pointSize() + 1))
            # name_font.setBold(True)
            name_label.setFont(name_font)
            name_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            # Increase value label font size as well and keep right alignment
            val_font = widget.font()
            val_font.setPointSize(max(9, val_font.pointSize() + 1))
            widget.setFont(val_font)
            widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            grid.addWidget(name_label, row, 0)
            grid.addWidget(widget, row, 1)

        # --- Begin 24-hour forecast area (Version-2.2) ---
        from PyQt6.QtWidgets import QScrollArea, QFrame

        forecast_header = QLabel("24-hour forecast:")
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

        # Forecast grid: 11 columns with combined Temp|Feels and Wind|Gusts as required
        forecast_grid = QGridLayout()
        forecast_grid.setVerticalSpacing(6)
        forecast_grid.setHorizontalSpacing(8)

        headers = [
            "Time",
            "Description",
            "Temp|Feels",
            "Humidity",
            "Cloud cover",
            "Rainfall",
            "Snowfall",
            "Precip.",
            "Wind|Gusts",
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

        # Create placeholders for 24 rows of forecast widgets; store references
        self._forecast_rows = []
        for row in range(1, 25):
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

        # --- End 24-hour forecast area ---

        # --- Begin 7-day forecast area (Version-4.3: card-based layout) ---
        daily_header = QLabel("7-day forecast:")
        dhf = daily_header.font()
        dhf.setPointSize(max(9, dhf.pointSize() + 2))
        dhf.setBold(True)
        daily_header.setFont(dhf)

        # Create a horizontal scroll area that will contain DayCard widgets arranged in a row.
        daily_scroll = QScrollArea()
        daily_scroll.setWidgetResizable(True)
        daily_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        daily_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        daily_container = QFrame()
        # Use an HBoxLayout so cards are laid out horizontally
        daily_hbox = QHBoxLayout()
        daily_hbox.setContentsMargins(0, 0, 0, 0)
        daily_hbox.setSpacing(10)
        daily_container.setLayout(daily_hbox)

        # Local small Card widget class defined inside __init__ to keep changes localized.
        class DayCardWidget(QFrame):
            def __init__(self) -> None:
                super().__init__()
                self.setFrameShape(QFrame.Shape.StyledPanel)
                self.setLineWidth(1)
                self.setFixedWidth(240)
                layout = QGridLayout()
                layout.setVerticalSpacing(6)
                layout.setHorizontalSpacing(8)
                layout.setContentsMargins(8, 8, 8, 8)

                # Date row (spans two columns) - make date label bold for readability
                self.date_label = QLabel("--")
                date_font = self.date_label.font()
                # date_font.setBold(True)
                date_font.setPointSize(max(10, date_font.pointSize() + 2))
                self.date_label.setFont(date_font)
                self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(self.date_label, 0, 0, 1, 2)

                # Icon + description (next row, spans two columns)
                self.icon_label = QLabel()
                # Increase icon size to 32x32 as required by Version-4.4
                self.icon_label.setFixedSize(32, 32)
                self.icon_label.setScaledContents(True)
                self.desc_label = QLabel("--")
                # Description text should be bold
                desc_font = self.desc_label.font()
                # desc_font.setBold(True)
                desc_font.setPointSize(max(10, desc_font.pointSize() + 2))
                self.desc_label.setFont(desc_font)
                self.desc_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                desc_widget = QWidget()
                desc_layout = QHBoxLayout()
                desc_layout.setContentsMargins(4, 0, 0, 0)
                # Add spacing so there is visible space between icon and description text
                desc_layout.setSpacing(8)
                desc_layout.addWidget(self.icon_label)
                desc_layout.addWidget(self.desc_label)
                desc_widget.setLayout(desc_layout)
                layout.addWidget(desc_widget, 1, 0, 1, 2)

                # Metrics: use two-column grid for label/value alignment (labels left, values right)
                # Column 0: label name, Column 1: value
                self.labels = {}
                metric_names = [
                    ("Tmax|Tmin", "--"),
                    ("Humid_max", "--"),
                    ("Cloud_max", "--"),
                    ("Rain_tot", "--"),
                    ("Snow_tot", "--"),
                    ("Precip_max", "--"),
                    ("Wind_mx|Gusts_mx", "--"),
                    ("Vis_min", "--"),
                    ("UV_max", "--"),
                    ("Sunrise|Sunset", "--"),
                ]
                row = 2
                for name, _ in metric_names:
                    name_lbl = QLabel(name.replace("|", " | "))
                    name_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    val_lbl = QLabel("--")
                    val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    layout.addWidget(name_lbl, row, 0)
                    layout.addWidget(val_lbl, row, 1)
                    self.labels[name] = val_lbl
                    row += 1

                self.setLayout(layout)

            def populate_from_dict(self, item: dict, main: "MainWindow") -> None:
                # Date
                self.date_label.setText(item.get("Date", "--"))

                # Icon
                svg_name = item.get("svg")
                if svg_name:
                    try:
                        # Load a larger pixmap (48px) for the card icon per Version-4.4
                        pix = main._load_svg_pixmap(svg_name, size=48)
                        if pix:
                            self.icon_label.setPixmap(pix)
                        else:
                            self.icon_label.clear()
                    except Exception:
                        self.icon_label.clear()
                else:
                    self.icon_label.clear()

                # Description text (parenthetical)
                desc_text = item.get("description")
                if desc_text:
                    self.desc_label.setText(f"({desc_text})")
                else:
                    self.desc_label.setText("--")

                def _fmt_daily(key, fmt):
                    val = item.get(key)
                    if val is None:
                        return "--"
                    try:
                        if isinstance(val, float):
                            return fmt.format(val)
                        return str(val)
                    except Exception:
                        return "--"

                # Tmax|Tmin
                tmax = _fmt_daily("Tmax", "{:.0f}°F")
                tmin = _fmt_daily("Tmin", "{:.0f}°F")
                self.labels["Tmax|Tmin"].setText(f"{tmax}|{tmin}")

                self.labels["Humid_max"].setText(_fmt_daily("Humid_max", "{:.0f}%"))
                self.labels["Cloud_max"].setText(_fmt_daily("Cloud_max", "{:.0f}%"))
                self.labels["Rain_tot"].setText(_fmt_daily("Rain_tot", "{:.2f} in"))
                self.labels["Snow_tot"].setText(_fmt_daily("Snow_tot", "{:.2f} in"))
                self.labels["Precip_max"].setText(_fmt_daily("Precip_max", "{:.0f}%"))

                # Wind|Gusts
                wind_val = item.get("Wind_max")
                gust_val = item.get("Gusts_max")
                if wind_val is None:
                    wind_text = "--"
                else:
                    try:
                        wind_text = f"{int(round(float(wind_val)))}mph"
                    except Exception:
                        wind_text = _fmt_daily("Wind_max", "{:.1f}mph")
                if gust_val is None:
                    gust_text = "--"
                else:
                    try:
                        gust_text = f"{int(round(float(gust_val)))}mph"
                    except Exception:
                        gust_text = _fmt_daily("Gusts_max", "{:.1f}mph")
                self.labels["Wind_mx|Gusts_mx"].setText(f"{wind_text}|{gust_text}")

                # Visibility and UV
                vis_val = item.get("Vis_min")
                if vis_val is None:
                    self.labels["Vis_min"].setText("--")
                else:
                    try:
                        self.labels["Vis_min"].setText(main._visibility_text(vis_val))
                    except Exception:
                        self.labels["Vis_min"].setText("--")

                uv_val = item.get("UV_max")
                if uv_val is None:
                    self.labels["UV_max"].setText("--")
                else:
                    try:
                        self.labels["UV_max"].setText(main._uv_text(uv_val))
                    except Exception:
                        self.labels["UV_max"].setText("--")

                # Sunrise|Sunset
                sunrise_val = item.get("Sunrise") or "--"
                sunset_val = item.get("Sunset") or "--"
                self.labels["Sunrise|Sunset"].setText(f"{sunrise_val}|{sunset_val}")

        # Pre-create 7 DayCard widgets and add them to the horizontal layout
        self._daily_cards = []
        for _ in range(7):
            card = DayCardWidget()
            self._daily_cards.append(card)
            daily_hbox.addWidget(card)

        # Add a stretch at the end so cards align to the left when there is
        # extra horizontal space.
        daily_hbox.addStretch()

        daily_scroll.setWidget(daily_container)
        # --- End 7-day forecast area ---

        # Build the tab widget and place existing sections into tabs. Per the
        # task requirements, we MOVE existing widgets into tabs rather than
        # recreating them.
        tabs = QTabWidget()

        # Increase tab label font size to make the tab names more prominent
        # per Version-4.1. Modify only the tab bar's font so other widgets remain
        # unaffected and layout logic is unchanged.
        try:
            tab_font = tabs.tabBar().font()
            tab_font.setPointSize(max(10, tab_font.pointSize() + 3))
            # tab_font.setBold(True)
            tabs.tabBar().setFont(tab_font)
        except Exception:
            # Defensive: if the tabBar is not yet available for some reason,
            # ignore and continue — this preserves existing behavior.
            pass

        # NOW tab: top row, grid, refresh button
        now_tab = QWidget()
        now_layout = QVBoxLayout()
        now_layout.setContentsMargins(0, 0, 0, 0)
        now_layout.setSpacing(8)
        now_layout.addLayout(time_row)
        now_layout.addLayout(top_row)
        now_layout.addLayout(grid)
        now_layout.addWidget(self.refresh_button)
        now_tab.setLayout(now_layout)
        tabs.addTab(now_tab, "NOW")

        # HOURLY tab: 24-hour forecast area
        hourly_tab = QWidget()
        hourly_layout = QVBoxLayout()
        hourly_layout.setContentsMargins(0, 0, 0, 0)
        hourly_layout.setSpacing(8)
        hourly_layout.addWidget(forecast_header)
        hourly_layout.addWidget(forecast_scroll)
        hourly_tab.setLayout(hourly_layout)
        tabs.addTab(hourly_tab, "HOURLY")

        # 7-DAY tab: daily forecast area
        daily_tab = QWidget()
        daily_tab_layout = QVBoxLayout()
        daily_tab_layout.setContentsMargins(0, 0, 0, 0)
        daily_tab_layout.setSpacing(8)
        daily_tab_layout.addWidget(daily_header)
        daily_tab_layout.addWidget(daily_scroll)
        daily_tab.setLayout(daily_tab_layout)
        tabs.addTab(daily_tab, "7-DAY")

        # Default tab is NOW (index 0)
        tabs.setCurrentIndex(0)

        main_layout.addWidget(tabs)
        self.setLayout(main_layout)

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

        # Update time_label on timer and when refreshing
        self._time_update_timer = QTimer(self)
        self._time_update_timer.setInterval(10 * 1000)  # update every 10 seconds
        self._time_update_timer.timeout.connect(self._update_time_label)
        self._time_update_timer.start()

        # Request an initial fetch to populate UI and set initial time
        self._update_time_label()
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

    def _load_svg_pixmap(self, svg_filename: str, size: int = 128) -> Optional[QPixmap]:
        """Load an SVG file from the icons directory and render it to a QPixmap.

        Returns a size x size QPixmap on success or None on failure. The SVG is
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
            pixmap = QPixmap(size, size)
            # Create a transparent pixmap and render the SVG into a centered
            # rectangle so aspect ratio is preserved and the icon is not
            # distorted.
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
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
        - "Moderate" if UV Index is more than 2 and less than or equal to 6
        - "High" if UV Index is more than 6 and less than or equal to 8
        - "Very High" if UV Index is more than 8 and less than or equal to 10
        - "Extreme" if UV Index is more than 10
        """
        try:
            u = float(uv_val)
        except Exception:
            return "--"
        if u <= 2:
            return "Low"
        if u <= 6:
            return "Moderate"
        if u <= 8:
            return "High"
        if u <= 10:
            return "Very High"
        return "Extreme"

    def _format_time_no_space(self, dt_obj: Optional[datetime]) -> str:
        """Format a datetime to 12-hour time with AM/PM and no space (e.g. "7:01AM").

        Accepts an aware or naive datetime. Returns "--" on failure.
        """
        if dt_obj is None:
            return "--"
        try:
            # Try platform-friendly %-I first (no leading zero)
            return dt_obj.strftime("%-I:%M%p")
        except Exception:
            # Fallback: use %I and strip leading zero
            try:
                return dt_obj.strftime("%I:%M%p").lstrip("0")
            except Exception:
                return "--"

    def _update_time_label(self) -> None:
        """Update the time_label with current local time and today's date.

        Format per CURRENT_TASK.md:
        - time: "%l:%M %P" (e.g. " 3:45 PM")
        - date: "%b %d %Y (%a)" (e.g. "Sep 15 2024 (Sun)")
        Combine: " 3:45 PM, Sep 15 2024 (Sun)"

        Use left-justified text and defensive formatting to avoid crashes on
        platforms with limited strftime support.
        """
        try:
            now = datetime.now()
            # time with leading space for single-digit hour to match example
            try:
                time_str = now.strftime("%I:%M %p").lstrip("0")
                # Ensure single-digit hour has a leading space (" 3:45 PM")
                if len(time_str) > 0 and time_str[0].isdigit() and time_str[0] != ' ':
                    time_str = ' ' + time_str
            except Exception:
                time_str = now.strftime("%H:%M")
            try:
                date_str = now.strftime("%b %d %Y (%a)")
            except Exception:
                date_str = now.strftime("%Y-%m-%d")
            self.time_label.setText(f"{time_str}, {date_str}")
        except Exception:
            # Non-fatal: keep previous value
            pass

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
            temp_text = "--°F"
            feels_text = "--°F"
            if "temperature_2m" in data:
                temp_text = f"{int(round(data['temperature_2m']))}°F"
                self.temp_label.setText(temp_text)
            if "apparent_temperature" in data:
                feels_text = f"{int(round(data['apparent_temperature']))}°F"
                self.feels_label.setText(feels_text)
            # Update combined label
            self.temp_feels_label.setText(f"{temp_text} | {feels_text}")

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
            wind_text = "--mph"
            gusts_text = "--mph"
            if "wind_speed" in data:
                try:
                    wind_text = f"{int(round(float(data['wind_speed'])))}mph"
                    self.wind_label.setText(wind_text)
                except Exception:
                    wind_text = f"{float(data['wind_speed']):.1f}mph"
                    self.wind_label.setText(wind_text)
            if "wind_gusts" in data:
                try:
                    gusts_text = f"{int(round(float(data['wind_gusts'])))}mph"
                    self.gusts_label.setText(gusts_text)
                except Exception:
                    gusts_text = f"{float(data['wind_gusts']):.1f}mph"
                    self.gusts_label.setText(gusts_text)
            # Update combined wind|gusts label
            self.wind_gusts_label.setText(f"{wind_text} | {gusts_text}")

            # Visibility and UV index — map to text categories per CURRENT_TASK.md
            if "visibility" in data:
                self.visibility_label.setText(self._visibility_text(data["visibility"]))
            if "uv_index" in data:
                self.uv_label.setText(self._uv_text(data["uv_index"]))

            # Hourly forecast: update forecast rows if present
            hourly = data.get("hourly")
            if hourly and isinstance(hourly, list):
                for i, item in enumerate(hourly[:24]):
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

                    temp_val = _fmt_num("Temp", "{:.0f}°F")
                    feels_val = _fmt_num("Feels", "{:.0f}°F")
                    cells["Temp|Feels"].setText(f"{temp_val}|{feels_val}")

                    cells["Humidity"].setText(_fmt_num("Humidity", "{:.0f}%"))
                    cells["Cloud cover"].setText(_fmt_num("Cloud cover", "{:.0f}%"))
                    cells["Rainfall"].setText(_fmt_num("Rainfall", "{:.2f} in"))
                    cells["Snowfall"].setText(_fmt_num("Snowfall", "{:.2f} in"))
                    cells["Precip."].setText(_fmt_num("Precip.", "{:.0f}%"))

                    # Wind and Gusts combined
                    wind_val = item.get("Wind")
                    gust_val = item.get("Gusts")
                    if wind_val is None:
                        wind_text = "--"
                    else:
                        try:
                            wind_text = f"{int(round(float(wind_val)))}mph"
                        except Exception:
                            wind_text = _fmt_num("Wind", "{:.1f}mph")
                    if gust_val is None:
                        gust_text = "--"
                    else:
                        try:
                            gust_text = f"{int(round(float(gust_val)))}mph"
                        except Exception:
                            gust_text = _fmt_num("Gusts", "{:.1f}mph")
                    cells["Wind|Gusts"].setText(f"{wind_text}|{gust_text}")

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

            # Daily forecast: update daily rows if present
            daily = data.get("daily")
            if daily and isinstance(daily, list):
                for i, item in enumerate(daily[:7]):
                    if i < len(self._daily_cards):
                        card = self._daily_cards[i]
                        card.populate_from_dict(item, self)

        except Exception as exc:
            # Defensive: show error but don't crash the application
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        """Show a critical message when the Worker reports a fetch failure.

        Errors are presented in a blocking QMessageBox so the user is clearly
        informed about transient network or API failures.
        """
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
