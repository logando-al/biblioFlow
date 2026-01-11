"""
Splash Screen

Shows a splash screen with logo and loading progress on startup.
"""
import os
from PyQt6.QtWidgets import QSplashScreen, QApplication, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont


class SplashScreen(QSplashScreen):
    """Animated splash screen with progress bar."""

    def __init__(self):
        # Load the icon
        icon_path = self._get_icon_path()
        if os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(
                300, 300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            # Fallback: create a simple colored pixmap
            pixmap = QPixmap(300, 300)
            pixmap.fill(QColor("#1A1A1A"))

        # Create a larger canvas for splash
        splash_pixmap = QPixmap(400, 450)
        splash_pixmap.fill(QColor("#0D0D0D"))

        # Paint the icon centered
        painter = QPainter(splash_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw icon
        x = (400 - pixmap.width()) // 2
        painter.drawPixmap(x, 30, pixmap)

        # Draw app name
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 350, 400, 40, Qt.AlignmentFlag.AlignCenter, "BiblioFlow")

        # Draw tagline
        painter.setPen(QColor("#3B82F6"))
        font = QFont("Segoe UI", 11)
        painter.setFont(font)
        painter.drawText(0, 385, 400, 30, Qt.AlignmentFlag.AlignCenter, "Research PDF Organizer")

        painter.end()

        super().__init__(splash_pixmap)
        self.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)

        # Progress bar
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 420, 300, 8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #1A1A1A;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 4px;
            }
        """)
        self.progress.setValue(0)

        self._progress_value = 0

    def _get_icon_path(self) -> str:
        """Get the icon path."""
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            return os.path.join(base_path, 'assets', 'icon.png')
        else:
            return os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')

    def set_progress(self, value: int):
        """Set the progress bar value (0-100)."""
        self._progress_value = value
        self.progress.setValue(value)
        QApplication.processEvents()

    def set_message(self, message: str):
        """Show a status message."""
        self.showMessage(
            message,
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
            QColor("#A0A0A0")
        )
        QApplication.processEvents()


def show_splash() -> SplashScreen:
    """Create and show the splash screen."""
    splash = SplashScreen()
    splash.show()
    QApplication.processEvents()
    return splash
