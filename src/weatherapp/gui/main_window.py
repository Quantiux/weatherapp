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
        self.temp_label = QLabel("--°F")
        self.desc_label = QLabel("Unknown")
        self.refresh_button = QPushButton("Refresh Now")

        # Layout: vertical stack for simplicity and clarity
        layout = QVBoxLayout()
        layout.addWidget(self.temp_label)
        layout.addWidget(self.desc_label)
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

        The Worker emits a minimal dict containing temperature_2m, weather_code,
        and is_day when available. We defensively extract those fields and update
        the labels. Any unexpected structure causes a non-fatal warning dialog.
        """
        try:
            # Update temperature label if available
            if "temperature_2m" in data:
                self.temp_label.setText(f"{int(round(data['temperature_2m']))}°F")

            # Update description label using helpers that map codes to strings/icons
            if "weather_code" in data:
                code = int(data["weather_code"])
                tod = "day" if data.get("is_day", True) else "night"
                svg = get_svg_for_code(code, tod)
                desc = get_desc_for_code(code)
                # Show a compact representation: icon (description)
                self.desc_label.setText(f"{svg} ({desc})")
        except Exception as exc:
            # Defensive: show error but don't crash the application
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        """Show a critical message when the Worker reports a fetch failure.

        Errors are presented in a blocking QMessageBox so the user is clearly
        informed about transient network or API failures.
        """
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
