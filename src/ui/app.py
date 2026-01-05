"""
Main Application Window

Central hub for BiblioFlow UI.
"""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import qtawesome as qta

from ..core.version import __version__, APP_NAME
from ..core.updater import UpdateChecker


class UpdateWorker(QThread):
    """Background thread for checking/downloading updates."""
    
    update_available = pyqtSignal(str, str)  # version, release_notes
    download_progress = pyqtSignal(int, int)  # downloaded, total
    download_complete = pyqtSignal(str)  # path to new exe
    error = pyqtSignal(str)
    
    def __init__(self, action="check"):
        super().__init__()
        self.action = action
        self.checker = UpdateChecker()
    
    def run(self):
        try:
            if self.action == "check":
                if self.checker.check_for_updates():
                    self.update_available.emit(
                        self.checker.latest_version,
                        self.checker.release_notes or ""
                    )
            elif self.action == "download":
                path = self.checker.download_update(
                    progress_callback=lambda d, t: self.download_progress.emit(d, t)
                )
                if path:
                    self.download_complete.emit(path)
                else:
                    self.error.emit("Download failed")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{__version__}")
        self.setMinimumSize(900, 600)
        self.update_checker = UpdateChecker()
        
        self._setup_ui()
        self._apply_styles()
        self._check_for_updates()
    
    def _setup_ui(self):
        """Initialize UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content area (will be StackedWidget for different views)
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)
        
        # Placeholder for drop zone (to be implemented)
        placeholder = QLabel("Drop Zone Coming Soon")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("font-size: 24px; color: #A0A0A0;")
        self.content_stack.addWidget(placeholder)
    
    def _create_header(self) -> QWidget:
        """Create header with navigation."""
        header = QWidget()
        header.setObjectName("header")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Logo/Title
        title = QLabel(APP_NAME)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Navigation buttons
        btn_drop = QPushButton(qta.icon('fa5s.cloud-upload-alt', color='white'), "Drop Zone")
        btn_library = QPushButton(qta.icon('fa5s.book', color='white'), "Library")
        btn_settings = QPushButton(qta.icon('fa5s.cog', color='white'), "Settings")
        
        for btn in [btn_drop, btn_library, btn_settings]:
            btn.setObjectName("nav-btn")
            layout.addWidget(btn)
        
        return header
    
    def _apply_styles(self):
        """Apply dark theme styles."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0D0D0D;
            }
            #header {
                background-color: #1A1A1A;
                border-bottom: 1px solid #333;
            }
            #nav-btn {
                background-color: transparent;
                border: none;
                color: white;
                padding: 8px 16px;
                font-size: 14px;
            }
            #nav-btn:hover {
                background-color: #1E3A5F;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #1E3A5F;
                border: 1px solid #3B82F6;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
    
    def _check_for_updates(self):
        """Check for updates on startup."""
        self.update_worker = UpdateWorker("check")
        self.update_worker.update_available.connect(self._on_update_available)
        self.update_worker.start()
    
    def _on_update_available(self, version: str, notes: str):
        """Handle update available notification."""
        reply = QMessageBox.question(
            self,
            "Update Available",
            f"A new version ({version}) is available.\n\nWould you like to update now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._start_update_download()
    
    def _start_update_download(self):
        """Start downloading the update."""
        self.progress = QProgressDialog("Downloading update...", "Cancel", 0, 100, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.show()
        
        self.download_worker = UpdateWorker("download")
        self.download_worker.checker = self.update_worker.checker
        self.download_worker.download_progress.connect(self._on_download_progress)
        self.download_worker.download_complete.connect(self._on_download_complete)
        self.download_worker.error.connect(self._on_download_error)
        self.download_worker.start()
    
    def _on_download_progress(self, downloaded: int, total: int):
        """Update download progress."""
        if total > 0:
            percent = int((downloaded / total) * 100)
            self.progress.setValue(percent)
    
    def _on_download_complete(self, path: str):
        """Handle download complete."""
        self.progress.close()
        
        reply = QMessageBox.information(
            self,
            "Download Complete",
            "Update downloaded. The application will restart to apply the update.",
            QMessageBox.StandardButton.Ok
        )
        
        # Apply update and exit
        if self.update_worker.checker.apply_update(path):
            QApplication.quit()
        else:
            QMessageBox.warning(
                self,
                "Update Failed",
                "Could not apply update. Please download manually from GitHub."
            )
    
    def _on_download_error(self, error: str):
        """Handle download error."""
        self.progress.close()
        QMessageBox.warning(
            self,
            "Update Error",
            f"Failed to download update: {error}"
        )


def run_app():
    """Run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(__version__)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
