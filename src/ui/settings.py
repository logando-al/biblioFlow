"""
Settings Panel

Configuration for output folder, naming format, etc.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QFileDialog,
    QGroupBox
)
from PyQt6.QtCore import Qt
import qtawesome as qta


class SettingsPanel(QWidget):
    """Settings configuration panel."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
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
        self.folder_input.setPlaceholderText("Select output folder...")
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
        format_layout.addWidget(self.format_combo)
        
        preview_label = QLabel("Preview: [2024] Smith, J. - Machine Learning.pdf")
        preview_label.setStyleSheet("color: #A0A0A0; font-style: italic;")
        format_layout.addWidget(preview_label)
        
        layout.addWidget(format_group)
        
        # Auto-update section
        update_group = QGroupBox("Updates")
        update_layout = QHBoxLayout(update_group)
        
        update_label = QLabel("Check for updates on startup")
        update_layout.addWidget(update_label)
        update_layout.addStretch()
        
        check_btn = QPushButton("Check Now")
        update_layout.addWidget(check_btn)
        
        layout.addWidget(update_group)
        
        layout.addStretch()
    
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
            QLabel {
                color: white;
            }
        """)
    
    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.folder_input.setText(folder)
