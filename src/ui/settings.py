"""
Settings Panel

Configuration for output folder, naming format, watch folder, etc.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFileDialog,
    QGroupBox, QCheckBox
)
from PyQt6.QtCore import pyqtSignal
import qtawesome as qta

from ..core.config import ConfigManager


class SettingsPanel(QWidget):
    """Settings configuration panel."""

    settings_changed = pyqtSignal()  # Emitted when settings change
    watch_folder_changed = pyqtSignal(bool, str)  # enabled, path
    check_updates_requested = pyqtSignal()  # Emitted when Check Now is clicked

    def __init__(self, config: ConfigManager = None):
        super().__init__()
        self.config = config or ConfigManager()
        self._setup_ui()
        self._load_settings()
        self._apply_styles()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Output folder section
        folder_group = QGroupBox("Output Folder")
        folder_layout = QHBoxLayout(folder_group)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select output folder for organized papers...")
        self.folder_input.textChanged.connect(self._on_output_folder_changed)
        folder_layout.addWidget(self.folder_input)

        browse_btn = QPushButton(qta.icon('fa5s.folder-open', color='white'), "Browse")
        browse_btn.clicked.connect(self._browse_folder)
        folder_layout.addWidget(browse_btn)

        layout.addWidget(folder_group)

        # Naming format section
        format_group = QGroupBox("Naming Format")
        format_layout = QVBoxLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "[Year] Author - Title.pdf",
            "Author_Year_Title.pdf",
            "Title (Year).pdf"
        ])
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        format_layout.addWidget(self.format_combo)

        self.preview_label = QLabel("Preview: [2024] Smith, J. - Machine Learning.pdf")
        self.preview_label.setStyleSheet("color: #A0A0A0; font-style: italic;")
        format_layout.addWidget(self.preview_label)

        layout.addWidget(format_group)

        # Watch folder section
        watch_group = QGroupBox("Watch Folder")
        watch_layout = QVBoxLayout(watch_group)

        self.watch_enabled = QCheckBox("Auto-process new PDFs in watch folder")
        self.watch_enabled.toggled.connect(self._on_watch_toggled)
        watch_layout.addWidget(self.watch_enabled)

        watch_path_layout = QHBoxLayout()
        self.watch_folder_input = QLineEdit()
        self.watch_folder_input.setPlaceholderText("Select folder to watch...")
        self.watch_folder_input.setEnabled(False)
        watch_path_layout.addWidget(self.watch_folder_input)

        self.watch_browse_btn = QPushButton(qta.icon('fa5s.folder-open', color='white'), "Browse")
        self.watch_browse_btn.clicked.connect(self._browse_watch_folder)
        self.watch_browse_btn.setEnabled(False)
        watch_path_layout.addWidget(self.watch_browse_btn)

        watch_layout.addLayout(watch_path_layout)
        layout.addWidget(watch_group)

        # Auto-update section
        update_group = QGroupBox("Updates")
        update_layout = QVBoxLayout(update_group)

        self.check_updates = QCheckBox("Check for updates on startup")
        self.check_updates.toggled.connect(self._on_check_updates_changed)
        update_layout.addWidget(self.check_updates)

        check_now_layout = QHBoxLayout()
        check_now_layout.addStretch()
        check_btn = QPushButton("Check Now")
        check_btn.clicked.connect(self._check_updates_now)
        check_now_layout.addWidget(check_btn)
        update_layout.addLayout(check_now_layout)

        layout.addWidget(update_group)

        # Default citation format
        citation_group = QGroupBox("Default Citation Format")
        citation_layout = QVBoxLayout(citation_group)

        self.citation_combo = QComboBox()
        self.citation_combo.addItems(["BibTeX", "APA 7th", "IEEE"])
        self.citation_combo.currentIndexChanged.connect(self._on_citation_format_changed)
        citation_layout.addWidget(self.citation_combo)

        layout.addWidget(citation_group)

        layout.addStretch()

        # Reset button
        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_btn = QPushButton(qta.icon('fa5s.undo', color='white'), "Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        reset_layout.addWidget(reset_btn)
        layout.addLayout(reset_layout)

    def _apply_styles(self):
        """Apply settings panel styles."""
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1A1A1A;
                border: 1px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                color: white;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
            QLineEdit {
                background-color: #0D0D0D;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }
            QLineEdit:disabled {
                color: #666;
            }
            QComboBox {
                background-color: #0D0D0D;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1A1A;
                border: 1px solid #333;
                color: white;
                selection-background-color: #1E3A5F;
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
            QPushButton:disabled {
                background-color: #333;
                border-color: #555;
                color: #666;
            }
            QLabel {
                color: white;
            }
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #333;
                background-color: #0D0D0D;
            }
            QCheckBox::indicator:checked {
                background-color: #3B82F6;
                border-color: #3B82F6;
            }
        """)

    def _load_settings(self):
        """Load settings from config."""
        self.folder_input.setText(self.config.get("output_folder", ""))

        format_map = {"default": 0, "underscore": 1, "title_first": 2}
        format_name = self.config.get("naming_format", "default")
        self.format_combo.setCurrentIndex(format_map.get(format_name, 0))

        self.watch_enabled.setChecked(self.config.get("watch_folder_enabled", False))
        self.watch_folder_input.setText(self.config.get("watch_folder_path", ""))

        self.check_updates.setChecked(self.config.get("check_updates_on_startup", True))

        citation_map = {"bibtex": 0, "apa7": 1, "ieee": 2}
        citation_format = self.config.get("default_citation_format", "bibtex")
        self.citation_combo.setCurrentIndex(citation_map.get(citation_format, 0))

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.folder_input.setText(folder)

    def _browse_watch_folder(self):
        """Open folder browser for watch folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Watch Folder")
        if folder:
            self.watch_folder_input.setText(folder)
            self._save_watch_folder()

    def _on_output_folder_changed(self, text):
        """Handle output folder change."""
        self.config.set("output_folder", text)
        self.settings_changed.emit()

    def _on_format_changed(self, index):
        """Handle naming format change."""
        formats = ["default", "underscore", "title_first"]
        self.config.set("naming_format", formats[index])

        previews = [
            "[2024] Smith, J. - Machine Learning.pdf",
            "Smith_2024_Machine Learning.pdf",
            "Machine Learning (2024).pdf"
        ]
        self.preview_label.setText(f"Preview: {previews[index]}")
        self.settings_changed.emit()

    def _on_watch_toggled(self, checked):
        """Handle watch folder toggle."""
        self.watch_folder_input.setEnabled(checked)
        self.watch_browse_btn.setEnabled(checked)
        self._save_watch_folder()

    def _save_watch_folder(self):
        """Save watch folder settings."""
        enabled = self.watch_enabled.isChecked()
        path = self.watch_folder_input.text()
        self.config.set("watch_folder_enabled", enabled)
        self.config.set("watch_folder_path", path)
        self.watch_folder_changed.emit(enabled, path)
        self.settings_changed.emit()

    def _on_check_updates_changed(self, checked):
        """Handle check updates toggle."""
        self.config.set("check_updates_on_startup", checked)
        self.settings_changed.emit()

    def _on_citation_format_changed(self, index):
        """Handle default citation format change."""
        formats = ["bibtex", "apa7", "ieee"]
        self.config.set("default_citation_format", formats[index])
        self.settings_changed.emit()

    def _check_updates_now(self):
        """Trigger update check."""
        self.check_updates_requested.emit()

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.config.reset_to_defaults()
        self._load_settings()
        self.settings_changed.emit()
