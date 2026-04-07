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
    """Minimal main window for WeatherApp (Version-0)."""

    # Expose a signal to request the worker to fetch (queued across threads)
    request_fetch = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("WeatherApp")

        self.temp_label = QLabel("--°F")
        self.desc_label = QLabel("Unknown")
        self.refresh_button = QPushButton("Refresh Now")

        layout = QVBoxLayout()
        layout.addWidget(self.temp_label)
        layout.addWidget(self.desc_label)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        # Worker thread setup
        self._thread: Optional[QThread] = QThread()
        self._worker = Worker()
        self._worker.moveToThread(self._thread)
        self.request_fetch.connect(self._worker.fetch)
        self._worker.weather_fetched.connect(self.on_weather_fetched)
        self._worker.fetch_failed.connect(self.on_fetch_failed)
        self._thread.start()

        # Connect UI actions
        self.refresh_button.clicked.connect(self.on_refresh_clicked)

        # Automatic refresh every 10 minutes
        self._timer = QTimer(self)
        self._timer.setInterval(10 * 60 * 1000)
        self._timer.timeout.connect(self.on_refresh_clicked)
        self._timer.start()

    def closeEvent(self, event) -> None:
        # Cleanly stop the worker thread
        try:
            self._thread.quit()
            self._thread.wait()
        except Exception:
            pass
        super().closeEvent(event)

    def on_refresh_clicked(self) -> None:
        # Request the worker to fetch via the queued signal
        self.request_fetch.emit()

    def on_weather_fetched(self, data: dict) -> None:
        try:
            if "temperature_2m" in data:
                self.temp_label.setText(f"{int(round(data['temperature_2m']))}°F")
            if "weather_code" in data:
                code = int(data["weather_code"])
                tod = "day" if data.get("is_day", True) else "night"
                svg = get_svg_for_code(code, tod)
                desc = get_desc_for_code(code)
                self.desc_label.setText(f"{svg} ({desc})")
        except Exception as exc:
            # Defensive: show error but don't crash
            QMessageBox.warning(self, "Display Error", f"Failed to display weather: {exc}")

    def on_fetch_failed(self, error_msg: str) -> None:
        QMessageBox.critical(self, "Fetch Failed", f"Weather fetch failed: {error_msg}")
