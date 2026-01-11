"""
Library Table View

Displays organized papers in a searchable table with citation copy and RIS export.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QHeaderView, QMenu,
    QPushButton, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
import qtawesome as qta

from ..core.metadata import PaperMetadata
from ..core.citations import (
    generate_bibtex, generate_apa7, generate_ieee,
    generate_ris, generate_ris_batch, copy_to_clipboard
)
from ..core.library_store import LibraryStore


class LibraryView(QWidget):
    """Library view showing all organized papers with citation features."""

    paper_opened = pyqtSignal(str)  # file path
    status_message = pyqtSignal(str)  # status bar message

    def __init__(self, library_store: LibraryStore = None):
        super().__init__()
        self.store = library_store or LibraryStore()
        self._paper_data = {}  # row -> paper dict
        self._setup_ui()
        self._load_papers()

    def _setup_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Toolbar
        toolbar = QHBoxLayout()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search papers...")
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input, 1)

        # Export buttons
        btn_export_selected = QPushButton(qta.icon('fa5s.file-export', color='white'), "Export Selected")
        btn_export_selected.clicked.connect(self._export_selected_ris)
        toolbar.addWidget(btn_export_selected)

        btn_export_all = QPushButton(qta.icon('fa5s.download', color='white'), "Export All")
        btn_export_all.clicked.connect(self._export_all_ris)
        toolbar.addWidget(btn_export_all)

        layout.addLayout(toolbar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Title", "Authors", "Year", "Journal", "DOI"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.doubleClicked.connect(self._on_double_click)
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
            QPushButton {
                background-color: #1E3A5F;
                border: 1px solid #3B82F6;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QMenu {
                background-color: #1A1A1A;
                border: 1px solid #333;
                color: white;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #1E3A5F;
            }
        """)

    def _load_papers(self):
        """Load papers from library store."""
        self.table.setRowCount(0)
        self._paper_data.clear()

        for paper in self.store.get_all():
            self._add_paper_row(paper)

    def _add_paper_row(self, paper: dict):
        """Add a paper to the table."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        authors = ", ".join(paper.get("authors", [])[:3])
        if len(paper.get("authors", [])) > 3:
            authors += " et al."

        self.table.setItem(row, 0, QTableWidgetItem(paper.get("title", "")))
        self.table.setItem(row, 1, QTableWidgetItem(authors))
        self.table.setItem(row, 2, QTableWidgetItem(str(paper.get("year", ""))))
        self.table.setItem(row, 3, QTableWidgetItem(paper.get("journal", "")))
        self.table.setItem(row, 4, QTableWidgetItem(paper.get("doi", "")))

        self._paper_data[row] = paper

    def add_paper(self, metadata: PaperMetadata, file_path: str):
        """Add a new paper to the library."""
        paper_id = self.store.add_paper(metadata, file_path)
        paper = self.store.get_paper(paper_id)
        if paper:
            self._add_paper_row(paper)

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

    def _show_context_menu(self, position):
        """Show right-click context menu."""
        row = self.table.rowAt(position.y())
        if row < 0:
            return

        menu = QMenu(self)

        # Citation copy actions
        copy_bibtex = QAction(qta.icon('fa5s.code', color='white'), "Copy BibTeX", self)
        copy_bibtex.triggered.connect(lambda: self._copy_citation(row, "bibtex"))
        menu.addAction(copy_bibtex)

        copy_apa = QAction(qta.icon('fa5s.quote-left', color='white'), "Copy APA 7th", self)
        copy_apa.triggered.connect(lambda: self._copy_citation(row, "apa7"))
        menu.addAction(copy_apa)

        copy_ieee = QAction(qta.icon('fa5s.microchip', color='white'), "Copy IEEE", self)
        copy_ieee.triggered.connect(lambda: self._copy_citation(row, "ieee"))
        menu.addAction(copy_ieee)

        menu.addSeparator()

        # Export actions
        export_ris = QAction(qta.icon('fa5s.file-export', color='white'), "Export to RIS", self)
        export_ris.triggered.connect(lambda: self._export_single_ris(row))
        menu.addAction(export_ris)

        menu.addSeparator()

        # Open file
        open_file = QAction(qta.icon('fa5s.external-link-alt', color='white'), "Open PDF", self)
        open_file.triggered.connect(lambda: self._open_pdf(row))
        menu.addAction(open_file)

        # Open folder
        open_folder = QAction(qta.icon('fa5s.folder-open', color='white'), "Show in Folder", self)
        open_folder.triggered.connect(lambda: self._open_folder(row))
        menu.addAction(open_folder)

        menu.exec(self.table.mapToGlobal(position))

    def _get_metadata_for_row(self, row: int) -> PaperMetadata:
        """Get PaperMetadata for a table row."""
        paper = self._paper_data.get(row, {})
        return self.store.to_metadata(paper)

    def _copy_citation(self, row: int, format_type: str):
        """Copy citation to clipboard."""
        metadata = self._get_metadata_for_row(row)

        if format_type == "bibtex":
            citation = generate_bibtex(metadata)
        elif format_type == "apa7":
            citation = generate_apa7(metadata)
        elif format_type == "ieee":
            citation = generate_ieee(metadata)
        else:
            return

        if copy_to_clipboard(citation):
            self.status_message.emit(f"Copied {format_type.upper()} citation to clipboard")

    def _export_single_ris(self, row: int):
        """Export single paper to RIS file."""
        metadata = self._get_metadata_for_row(row)
        ris_content = generate_ris(metadata)

        filename = f"{metadata.first_author}_{metadata.year or 'unknown'}.ris"
        path, _ = QFileDialog.getSaveFileName(
            self, "Export to RIS", filename, "RIS Files (*.ris)"
        )

        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(ris_content)
                self.status_message.emit(f"Exported to {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _export_selected_ris(self):
        """Export selected papers to RIS file."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select papers to export.")
            return

        papers = [self._get_metadata_for_row(row) for row in selected_rows]
        ris_content = generate_ris_batch(papers)

        path, _ = QFileDialog.getSaveFileName(
            self, "Export Selected to RIS", "selected_papers.ris", "RIS Files (*.ris)"
        )

        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(ris_content)
                self.status_message.emit(f"Exported {len(papers)} papers to {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _export_all_ris(self):
        """Export all papers to RIS file."""
        papers = self.store.get_all_as_metadata()
        if not papers:
            QMessageBox.information(self, "Empty Library", "No papers to export.")
            return

        ris_content = generate_ris_batch(papers)

        path, _ = QFileDialog.getSaveFileName(
            self, "Export All to RIS", "library_export.ris", "RIS Files (*.ris)"
        )

        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(ris_content)
                self.status_message.emit(f"Exported {len(papers)} papers to {os.path.basename(path)}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", str(e))

    def _open_pdf(self, row: int):
        """Open the PDF file."""
        paper = self._paper_data.get(row, {})
        file_path = paper.get("file_path", "")
        if file_path and os.path.exists(file_path):
            os.startfile(file_path)
        else:
            QMessageBox.warning(self, "File Not Found", "The PDF file could not be found.")

    def _open_folder(self, row: int):
        """Open the folder containing the PDF."""
        paper = self._paper_data.get(row, {})
        file_path = paper.get("file_path", "")
        if file_path and os.path.exists(file_path):
            folder = os.path.dirname(file_path)
            os.startfile(folder)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder could not be found.")

    def _on_double_click(self, index):
        """Handle double-click to open PDF."""
        self._open_pdf(index.row())

    def refresh(self):
        """Refresh the library view."""
        self._load_papers()
