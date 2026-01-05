"""
Library Table View

Displays organized papers in a searchable table.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QHeaderView
)
from PyQt6.QtCore import Qt
import qtawesome as qta


class LibraryView(QWidget):
    """Library view showing all organized papers."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search papers...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Authors", "Year", "Journal", "DOI"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self._apply_styles()
    
    def _apply_styles(self):
        """Apply table styles."""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #1A1A1A;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3B82F6;
            }
            QTableWidget {
                background-color: #1A1A1A;
                border: none;
                color: white;
                gridline-color: #333;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #1E3A5F;
            }
            QHeaderView::section {
                background-color: #0D0D0D;
                color: #A0A0A0;
                border: none;
                padding: 10px;
                font-weight: bold;
            }
        """)
    
    def _on_search(self, text: str):
        """Filter table based on search text."""
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)
    
    def add_paper(self, title: str, authors: str, year: str, journal: str, doi: str):
        """Add a paper to the library."""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(title))
        self.table.setItem(row, 1, QTableWidgetItem(authors))
        self.table.setItem(row, 2, QTableWidgetItem(year))
        self.table.setItem(row, 3, QTableWidgetItem(journal))
        self.table.setItem(row, 4, QTableWidgetItem(doi))
