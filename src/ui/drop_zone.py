"""
Drag-and-Drop Zone Widget

Handles PDF file drops with glow effects.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor, QMouseEvent
import qtawesome as qta


class DropZone(QWidget):
    """Widget for drag-and-drop PDF files with glow effects."""

    files_dropped = pyqtSignal(list)  # List of file paths

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._glow_intensity = 0.0
        self._is_dragging = False
        self._setup_ui()
        self._setup_glow_effect()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        self.icon_label = QLabel()
        self.icon_label.setPixmap(qta.icon('fa5s.cloud-upload-alt', color='#3B82F6').pixmap(64, 64))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.icon_label)

        # Text
        self.text_label = QLabel("Drop PDF files here")
        self.text_label.setStyleSheet("font-size: 18px; color: #A0A0A0; margin-top: 10px;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)

        self.subtext_label = QLabel("or click to browse")
        self.subtext_label.setStyleSheet("font-size: 14px; color: #666;")
        self.subtext_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtext_label)

        self._apply_styles()

    def _setup_glow_effect(self):
        """Setup the glow drop shadow effect."""
        self.glow_effect = QGraphicsDropShadowEffect(self)
        self.glow_effect.setBlurRadius(10)
        self.glow_effect.setColor(QColor(59, 130, 246, 180))  # #3B82F6 with alpha
        self.glow_effect.setOffset(0, 0)
        self.setGraphicsEffect(self.glow_effect)

        # Glow animation for drag hover
        self.glow_animation = QPropertyAnimation(self, b"glowIntensity")
        self.glow_animation.setDuration(200)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(float)
    def glowIntensity(self):
        return self._glow_intensity

    @glowIntensity.setter
    def glowIntensity(self, value):
        self._glow_intensity = value
        self.glow_effect.setBlurRadius(value)

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
                background-color: #1E293B;
            }
            DropZone[dragging="true"] {
                border: 3px solid #60A5FA;
                background-color: #1E3A5F;
            }
        """)

    def _animate_glow_in(self):
        """Animate glow when dragging over."""
        self.glow_animation.stop()
        self.glow_animation.setStartValue(self.glow_effect.blurRadius())
        self.glow_animation.setEndValue(40)
        self.glow_animation.start()
        self.glow_effect.setColor(QColor(96, 165, 250, 220))  # Brighter blue

    def _animate_glow_out(self):
        """Animate glow back to normal."""
        self.glow_animation.stop()
        self.glow_animation.setStartValue(self.glow_effect.blurRadius())
        self.glow_animation.setEndValue(10)
        self.glow_animation.start()
        self.glow_effect.setColor(QColor(59, 130, 246, 180))

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter with glow animation."""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith('.pdf'):
                    event.acceptProposedAction()
                    self._is_dragging = True
                    self.setProperty("dragging", True)
                    self.style().polish(self)
                    self._animate_glow_in()
                    # Update icon color
                    self.icon_label.setPixmap(
                        qta.icon('fa5s.cloud-upload-alt', color='#60A5FA').pixmap(72, 72)
                    )
                    return

    def dragLeaveEvent(self, event):
        """Handle drag leave."""
        self._is_dragging = False
        self.setProperty("dragging", False)
        self.style().polish(self)
        self._animate_glow_out()
        self.icon_label.setPixmap(
            qta.icon('fa5s.cloud-upload-alt', color='#3B82F6').pixmap(64, 64)
        )

    def dropEvent(self, event: QDropEvent):
        """Handle file drop."""
        self._is_dragging = False
        self.setProperty("dragging", False)
        self.style().polish(self)
        self._animate_glow_out()
        self.icon_label.setPixmap(
            qta.icon('fa5s.cloud-upload-alt', color='#3B82F6').pixmap(64, 64)
        )

        pdf_files = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith('.pdf'):
                pdf_files.append(path)

        if pdf_files:
            self.files_dropped.emit(pdf_files)

    def mousePressEvent(self, event: QMouseEvent):
        """Handle click to open file dialog."""
        if event.button() == Qt.MouseButton.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select PDF Files",
                "",
                "PDF Files (*.pdf)"
            )
            if files:
                self.files_dropped.emit(files)
