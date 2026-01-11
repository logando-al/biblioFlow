"""
System Tray Integration

Allows BiblioFlow to run in the system tray.
"""
import os
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class SystemTray(QObject):
    """System tray icon with menu."""

    show_window = pyqtSignal()
    quit_app = pyqtSignal()
    toggle_watch = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = None
        self._watch_enabled = False
        self._setup_tray()

    def _setup_tray(self):
        """Setup system tray icon and menu."""
        self.tray_icon = QSystemTrayIcon(self.parent())

        # Set icon
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("BiblioFlow - Research PDF Organizer")

        # Create menu
        menu = QMenu()

        # Show/Hide action
        show_action = QAction("Show BiblioFlow", menu)
        show_action.triggered.connect(self.show_window.emit)
        menu.addAction(show_action)

        menu.addSeparator()

        # Watch folder toggle
        self.watch_action = QAction("Watch Folder: Off", menu)
        self.watch_action.setCheckable(True)
        self.watch_action.triggered.connect(self._on_watch_toggled)
        menu.addAction(self.watch_action)

        menu.addSeparator()

        # Quit action
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)

        # Double-click to show window
        self.tray_icon.activated.connect(self._on_activated)

    def _get_icon_path(self) -> str:
        """Get the icon path."""
        import sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            return os.path.join(base_path, 'assets', 'icon.png')
        else:
            return os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.png')

    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window.emit()

    def _on_watch_toggled(self, checked):
        """Handle watch folder toggle."""
        self._watch_enabled = checked
        self.watch_action.setText(f"Watch Folder: {'On' if checked else 'Off'}")
        self.toggle_watch.emit(checked)

    def set_watch_enabled(self, enabled: bool):
        """Update watch folder state from settings."""
        self._watch_enabled = enabled
        self.watch_action.setChecked(enabled)
        self.watch_action.setText(f"Watch Folder: {'On' if enabled else 'Off'}")

    def show(self):
        """Show the tray icon."""
        if self.tray_icon:
            self.tray_icon.show()

    def hide(self):
        """Hide the tray icon."""
        if self.tray_icon:
            self.tray_icon.hide()

    def show_message(self, title: str, message: str, icon=QSystemTrayIcon.MessageIcon.Information):
        """Show a tray notification."""
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, 3000)

    @property
    def is_available(self) -> bool:
        """Check if system tray is available."""
        return QSystemTrayIcon.isSystemTrayAvailable()
