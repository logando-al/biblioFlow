"""
Main Application Window

Central hub for BiblioFlow UI - integrates all views and processing.
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QMessageBox, QProgressDialog, QStatusBar, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon
import qtawesome as qta

from ..core.version import __version__, APP_NAME
from ..core.updater import UpdateChecker
from ..core.config import ConfigManager
from ..core.processor import PDFProcessor, ProcessingResult
from ..core.library_store import LibraryStore
from ..core.watcher import FolderWatcher

from .drop_zone import DropZone
from .library import LibraryView
from .settings import SettingsPanel
from .queue_widget import QueueWidget
from .preview_card import PreviewCard


class UpdateWorker(QThread):
    """Background thread for checking/downloading updates."""
    
    update_available = pyqtSignal(str, str)
    download_progress = pyqtSignal(int, int)
    download_complete = pyqtSignal(str)
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
        self.setMinimumSize(1000, 700)
        
        # Initialize core components
        self.config = ConfigManager()
        self.library_store = LibraryStore()
        self.processor = PDFProcessor()
        self.watcher = FolderWatcher()
        self.update_checker = UpdateChecker()
        
        # Pending confirmation results
        self._pending_results = {}
        
        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        self._setup_watcher()
        
        if self.config.get("check_updates_on_startup", True):
            self._check_for_updates()
    
    def _setup_ui(self):
        """Initialize UI components."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setHandleWidth(1)
        
        # Left side: Content views
        self.content_stack = QStackedWidget()
        
        # Create views
        self.drop_zone_view = self._create_drop_zone_view()
        self.library_view = LibraryView(self.library_store)
        self.settings_view = SettingsPanel(self.config)
        
        self.content_stack.addWidget(self.drop_zone_view)
        self.content_stack.addWidget(self.library_view)
        self.content_stack.addWidget(self.settings_view)
        
        content_splitter.addWidget(self.content_stack)
        
        # Right side: Processing queue
        self.queue_widget = QueueWidget()
        self.queue_widget.setFixedWidth(300)
        content_splitter.addWidget(self.queue_widget)
        
        layout.addWidget(content_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #0D0D0D; color: #A0A0A0;")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
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
        self.btn_drop = QPushButton(qta.icon('fa5s.cloud-upload-alt', color='white'), "Drop Zone")
        self.btn_library = QPushButton(qta.icon('fa5s.book', color='white'), "Library")
        self.btn_settings = QPushButton(qta.icon('fa5s.cog', color='white'), "Settings")
        
        self.nav_buttons = [self.btn_drop, self.btn_library, self.btn_settings]
        
        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("nav-btn")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self._switch_view(idx))
            layout.addWidget(btn)
        
        # Set initial active state
        self.btn_drop.setChecked(True)
        
        return header
    
    def _create_drop_zone_view(self) -> QWidget:
        """Create the drop zone view with queue."""
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Drop zone
        self.drop_zone = DropZone()
        layout.addWidget(self.drop_zone, 1)
        
        return view
    
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
                border-radius: 6px;
            }
            #nav-btn:hover {
                background-color: #1E3A5F;
            }
            #nav-btn:checked {
                background-color: #1E3A5F;
                border: 1px solid #3B82F6;
            }
            QSplitter::handle {
                background-color: #333;
            }
        """)
    
    def _connect_signals(self):
        """Connect all signals."""
        # Drop zone
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        
        # Processor
        self.processor.processing_started.connect(self._on_processing_started)
        self.processor.metadata_found.connect(self._on_metadata_found)
        self.processor.confirmation_needed.connect(self._on_confirmation_needed)
        self.processor.processing_complete.connect(self._on_processing_complete)
        self.processor.processing_failed.connect(self._on_processing_failed)
        self.processor.batch_progress.connect(self._on_batch_progress)
        
        # Library
        self.library_view.status_message.connect(self._show_status)
        
        # Settings
        self.settings_view.watch_folder_changed.connect(self._on_watch_folder_changed)
        
        # Watcher
        self.watcher.new_file_detected.connect(self._on_watched_file_detected)
        self.watcher.error.connect(lambda e: self._show_status(f"Watch error: {e}"))
    
    def _setup_watcher(self):
        """Setup folder watcher from config."""
        if self.config.is_watch_folder_enabled():
            path = self.config.get_watch_folder_path()
            if path and os.path.isdir(path):
                self.watcher.set_watch_path(path)
                self.watcher.start()
                self._show_status(f"Watching: {path}")
    
    def _switch_view(self, index: int):
        """Switch to a different view."""
        self.content_stack.setCurrentIndex(index)
        
        # Update nav button states
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    
    def _on_files_dropped(self, file_paths: list):
        """Handle files dropped onto drop zone."""
        # Add to queue
        for path in file_paths:
            filename = os.path.basename(path)
            self.queue_widget.add_file(filename)
        
        # Configure processor
        self.processor.set_files(file_paths)
        self.processor.set_output_folder(self.config.get_output_folder())
        self.processor.set_naming_format(self.config.get_naming_format())
        self.processor.set_auto_confirm(False)
        
        # Start processing
        self.processor.start()
    
    def _on_processing_started(self, filename: str):
        """Handle processing started."""
        self.queue_widget.update_status(filename, "extracting")
        self._show_status(f"Processing: {filename}")
    
    def _on_metadata_found(self, filename: str, metadata):
        """Handle metadata found."""
        self.queue_widget.update_status(filename, "querying")
    
    def _on_confirmation_needed(self, result: ProcessingResult):
        """Show preview card for confirmation."""
        self.queue_widget.update_status(result.filename, "confirming")
        
        # Store result for later confirmation
        self._pending_results[result.filename] = result
        
        # Show preview dialog
        dialog = PreviewCard(result.filename, result.metadata, self)
        if dialog.exec():
            # User confirmed
            custom_filename = dialog.get_new_filename()
            self.processor.confirm_result(result, custom_filename)
        else:
            # User cancelled
            self.queue_widget.update_status(result.filename, "error")
            self._show_status(f"Cancelled: {result.filename}")
    
    def _on_processing_complete(self, old_path: str, new_path: str):
        """Handle file processing complete."""
        filename = os.path.basename(old_path)
        self.queue_widget.update_status(filename, "complete")
        
        # Get result and add to library
        result = self._pending_results.pop(filename, None)
        if result and result.metadata:
            self.library_view.add_paper(result.metadata, new_path)
        
        self._show_status(f"Organized: {os.path.basename(new_path)}")
    
    def _on_processing_failed(self, filename: str, error: str):
        """Handle processing failure."""
        self.queue_widget.update_status(filename, "error")
        self._show_status(f"Failed: {filename} - {error}")
    
    def _on_batch_progress(self, current: int, total: int):
        """Handle batch progress update."""
        self.queue_widget.set_batch_progress(current, total)
    
    def _on_watch_folder_changed(self, enabled: bool, path: str):
        """Handle watch folder settings change."""
        if enabled and path and os.path.isdir(path):
            self.watcher.set_watch_path(path)
            self.watcher.start()
            self._show_status(f"Watching: {path}")
        else:
            self.watcher.stop()
            self._show_status("Watch folder disabled")
    
    def _on_watched_file_detected(self, file_path: str):
        """Handle new file detected in watched folder."""
        self._show_status(f"New file detected: {os.path.basename(file_path)}")
        self._on_files_dropped([file_path])
    
    def _show_status(self, message: str):
        """Show message in status bar."""
        self.status_bar.showMessage(message, 5000)
    
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
        
        QMessageBox.information(
            self,
            "Download Complete",
            "Update downloaded. The application will restart to apply the update.",
            QMessageBox.StandardButton.Ok
        )
        
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
