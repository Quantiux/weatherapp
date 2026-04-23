"""Application entry point for WeatherApp.

This module provides a minimal CLI entry point that constructs the
QApplication instance and shows the MainWindow. It intentionally performs
no heavy work at import time so the module can be imported for testing and
static analysis without triggering network calls or GUI side-effects.
"""

from PyQt6.QtWidgets import QApplication
import sys

from weatherapp.gui.main_window import MainWindow


def main() -> None:
    """Create the QApplication, show the main window, and start the event loop.

    This function exits the process when the Qt event loop ends. It is safe to
    call from a console entry point and intentionally avoids performing any
    blocking or long-running operations.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
