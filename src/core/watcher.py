"""
Folder Watcher

Watches a folder for new PDF files and triggers processing.
"""
import os
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtCore import QFileSystemWatcher


class FolderWatcher(QObject):
    """
    Watches a folder for new PDF files.

    Uses QFileSystemWatcher for efficient file system monitoring.
    When a new PDF is detected, emits new_file_detected signal.
    """

    new_file_detected = pyqtSignal(str)  # file path
    error = pyqtSignal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._watcher = QFileSystemWatcher(self)
        self._watch_path = ""
        self._known_files = set()
        self._enabled = False

        # Debounce timer to avoid processing partially written files
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._check_for_new_files)
        self._pending_check = False

        self._watcher.directoryChanged.connect(self._on_directory_changed)

    def set_watch_path(self, path: str):
        """
        Set the folder to watch.

        Args:
            path: Path to the folder to watch
        """
        # Remove old path if any
        if self._watch_path and self._watch_path in self._watcher.directories():
            self._watcher.removePath(self._watch_path)

        self._watch_path = os.path.expanduser(path)

        if self._watch_path and os.path.isdir(self._watch_path):
            self._watcher.addPath(self._watch_path)
            self._scan_existing_files()

    def _scan_existing_files(self):
        """Scan folder for existing PDF files to establish baseline."""
        self._known_files.clear()

        if not self._watch_path or not os.path.isdir(self._watch_path):
            return

        try:
            for filename in os.listdir(self._watch_path):
                if filename.lower().endswith('.pdf'):
                    self._known_files.add(filename)
        except Exception as e:
            self.error.emit(f"Error scanning folder: {e}")

    def start(self):
        """Start watching the folder."""
        self._enabled = True
        if self._watch_path:
            self._scan_existing_files()

    def stop(self):
        """Stop watching the folder."""
        self._enabled = False
        self._debounce_timer.stop()

    def _on_directory_changed(self, path: str):
        """Handle directory change notification."""
        if not self._enabled:
            return

        # Use debounce timer to wait for file write to complete
        self._pending_check = True
        self._debounce_timer.start(500)  # 500ms debounce

    def _check_for_new_files(self):
        """Check for new PDF files in the watched folder."""
        if not self._enabled or not self._watch_path:
            return

        try:
            current_files = set()
            for filename in os.listdir(self._watch_path):
                if filename.lower().endswith('.pdf'):
                    current_files.add(filename)

            # Find new files
            new_files = current_files - self._known_files

            for filename in new_files:
                file_path = os.path.join(self._watch_path, filename)

                # Check if file is accessible (not still being written)
                if self._is_file_ready(file_path):
                    self.new_file_detected.emit(file_path)

            # Update known files
            self._known_files = current_files

        except Exception as e:
            self.error.emit(f"Error checking for new files: {e}")

    def _is_file_ready(self, file_path: str) -> bool:
        """Check if a file is ready to be processed (not locked)."""
        try:
            with open(file_path, 'rb') as f:
                f.read(1)  # Try to read first byte
            return True
        except (IOError, PermissionError):
            return False

    @property
    def is_watching(self) -> bool:
        """Check if currently watching a folder."""
        return self._enabled and bool(self._watch_path)

    @property
    def watch_path(self) -> str:
        """Get the current watch path."""
        return self._watch_path
