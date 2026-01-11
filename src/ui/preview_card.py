"""
Preview Card Dialog

Shows metadata preview before confirming file organization.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit
)
import qtawesome as qta

from ..core.metadata import PaperMetadata
from ..core.organizer import generate_filename


class PreviewCard(QDialog):
    """Dialog showing paper metadata preview."""

    def __init__(self, original_name: str, metadata: PaperMetadata, parent=None):
        super().__init__(parent)
        self.metadata = metadata
        self.original_name = original_name
        self.confirmed = False

        self.setWindowTitle("Confirm Rename")
        self.setMinimumWidth(500)
        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Original name
        orig_layout = QHBoxLayout()
        orig_icon = QLabel()
        orig_icon.setPixmap(qta.icon('fa5s.file-pdf', color='#EF4444').pixmap(24, 24))
        orig_layout.addWidget(orig_icon)
        orig_label = QLabel(f"Original: {self.original_name}")
        orig_label.setStyleSheet("color: #A0A0A0;")
        orig_layout.addWidget(orig_label)
        orig_layout.addStretch()
        layout.addLayout(orig_layout)

        # New name
        new_layout = QHBoxLayout()
        new_icon = QLabel()
        new_icon.setPixmap(qta.icon('fa5s.magic', color='#22C55E').pixmap(24, 24))
        new_layout.addWidget(new_icon)

        self.new_name_edit = QLineEdit(generate_filename(self.metadata))
        new_layout.addWidget(self.new_name_edit)
        layout.addLayout(new_layout)

        # Metadata details
        details = [
            ("fa5s.user", f"Authors: {self.metadata.author_string}"),
            ("fa5s.calendar", f"Year: {self.metadata.year or 'Unknown'}"),
            ("fa5s.book", f"Journal: {self.metadata.journal or 'Unknown'}"),
        ]

        for icon_name, text in details:
            row = QHBoxLayout()
            icon = QLabel()
            icon.setPixmap(qta.icon(icon_name, color='#3B82F6').pixmap(16, 16))
            row.addWidget(icon)
            label = QLabel(text)
            label.setStyleSheet("color: #A0A0A0; font-size: 13px;")
            row.addWidget(label)
            row.addStretch()
            layout.addLayout(row)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton(qta.icon('fa5s.times', color='white'), "Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_edit = QPushButton(qta.icon('fa5s.edit', color='white'), "Edit")
        self.btn_edit.clicked.connect(self._toggle_edit)
        btn_layout.addWidget(self.btn_edit)

        self.btn_confirm = QPushButton(qta.icon('fa5s.check', color='white'), "Confirm")
        self.btn_confirm.clicked.connect(self._confirm)
        self.btn_confirm.setObjectName("confirm-btn")
        btn_layout.addWidget(self.btn_confirm)

        layout.addLayout(btn_layout)

    def _apply_styles(self):
        """Apply dialog styles."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1A1A1A;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #0D0D0D;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px;
                color: white;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QPushButton {
                background-color: #333;
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            #confirm-btn {
                background-color: #1E3A5F;
                border: 1px solid #3B82F6;
            }
            #confirm-btn:hover {
                background-color: #2563EB;
            }
        """)

    def _toggle_edit(self):
        """Toggle edit mode for filename."""
        self.new_name_edit.setFocus()
        self.new_name_edit.selectAll()

    def _confirm(self):
        """Confirm the rename."""
        self.confirmed = True
        self.accept()

    def get_new_filename(self) -> str:
        """Get the (possibly edited) new filename."""
        return self.new_name_edit.text()
