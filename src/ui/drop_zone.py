"""
Drag-and-Drop Zone Widget

Handles PDF file drops for processing.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import qtawesome as qta


class DropZone(QWidget):
    """Widget for drag-and-drop PDF files."""

    files_dropped = pyqtSignal(list)  # List of file paths

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.cloud-upload-alt', color='#3B82F6').pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Text
        text = QLabel("Drop PDF files here")
        text.setStyleSheet("font-size: 18px; color: #A0A0A0; margin-top: 10px;")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text)

        subtext = QLabel("or click to browse")
        subtext.setStyleSheet("font-size: 14px; color: #666;")
        subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtext)

        self._apply_styles()

    def _apply_styles(self):
        """Apply drop zone styles."""
        self.setStyleSheet("""
            DropZone {
                background-color: #1A1A1A;
                border: 2px dashed #3B82F6;
                border-radius: 12px;
                min-height: 200px;
            }
            DropZone:hover {
                border-color: #60A5FA;
                background-color: #1E3A5F;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            # Check if any URLs are PDFs
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    self.setProperty("dragging", True)
                    self.style().polish(self)
                    return

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self.setProperty("dragging", False)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        """Handle file drop."""
        self.setProperty("dragging", False)
        self.style().polish(self)

        pdf_files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.pdf'):
                pdf_files.append(path)

        if pdf_files:
            self.files_dropped.emit(pdf_files)
