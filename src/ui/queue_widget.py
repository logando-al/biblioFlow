"""
Processing Queue Widget

Displays the queue of files being processed with status indicators.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
import qtawesome as qta


class QueueItem(QFrame):
    """Single item in the processing queue."""

    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        self.filename = filename
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI."""
        self.setObjectName("queue-item")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Status icon
        self.status_icon = QLabel()
        self.set_status("pending")
        layout.addWidget(self.status_icon)

        # Filename
        self.filename_label = QLabel(self.filename)
        self.filename_label.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(self.filename_label, 1)

        # Status text
        self.status_label = QLabel("Pending")
        self.status_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        layout.addWidget(self.status_label)

        self._apply_styles()

    def _apply_styles(self):
        """Apply item styles."""
        self.setStyleSheet("""
            #queue-item {
                background-color: #1A1A1A;
                border: 1px solid #333;
                border-radius: 6px;
                margin-bottom: 4px;
            }
        """)

    def set_status(self, status: str):
        """
        Set the status of this queue item.

        Args:
            status: One of 'pending', 'extracting', 'querying', 'confirming', 'complete', 'error'
        """
        icons = {
            "pending": ("fa5s.clock", "#666"),
            "extracting": ("fa5s.file-pdf", "#3B82F6"),
            "querying": ("fa5s.search", "#3B82F6"),
            "confirming": ("fa5s.question-circle", "#F59E0B"),
            "complete": ("fa5s.check-circle", "#22C55E"),
            "error": ("fa5s.times-circle", "#EF4444"),
        }

        labels = {
            "pending": "Pending",
            "extracting": "Extracting DOI...",
            "querying": "Fetching metadata...",
            "confirming": "Awaiting confirmation",
            "complete": "Complete",
            "error": "Failed",
        }

        icon_name, color = icons.get(status, icons["pending"])
        self.status_icon.setPixmap(qta.icon(icon_name, color=color).pixmap(16, 16))
        self.status_label.setText(labels.get(status, "Unknown"))


class QueueWidget(QWidget):
    """Widget showing the processing queue."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = {}
        self._setup_ui()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QHBoxLayout()
        title = QLabel("Processing Queue")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        header.addWidget(title)

        self.count_label = QLabel("0 items")
        self.count_label.setStyleSheet("color: #A0A0A0; font-size: 12px;")
        header.addWidget(self.count_label)
        header.addStretch()

        layout.addLayout(header)

        # Progress bar (for batch operations)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0D0D0D;
                border: 1px solid #333;
                border-radius: 4px;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Scroll area for queue items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        self.queue_container = QWidget()
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.setContentsMargins(0, 0, 0, 0)
        self.queue_layout.setSpacing(4)
        self.queue_layout.addStretch()

        scroll.setWidget(self.queue_container)
        layout.addWidget(scroll)

    def add_file(self, filename: str) -> QueueItem:
        """Add a file to the queue."""
        item = QueueItem(filename)
        self._items[filename] = item

        # Insert before the stretch
        self.queue_layout.insertWidget(self.queue_layout.count() - 1, item)
        self._update_count()

        return item

    def update_status(self, filename: str, status: str):
        """Update the status of a file in the queue."""
        if filename in self._items:
            self._items[filename].set_status(status)

    def remove_file(self, filename: str):
        """Remove a file from the queue."""
        if filename in self._items:
            item = self._items.pop(filename)
            self.queue_layout.removeWidget(item)
            item.deleteLater()
            self._update_count()

    def clear(self):
        """Clear all items from the queue."""
        for filename in list(self._items.keys()):
            self.remove_file(filename)

    def set_batch_progress(self, current: int, total: int):
        """Set batch processing progress."""
        if total > 1:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        else:
            self.progress_bar.setVisible(False)

    def _update_count(self):
        """Update the item count label."""
        count = len(self._items)
        self.count_label.setText(f"{count} item{'s' if count != 1 else ''}")

    @property
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._items) == 0
