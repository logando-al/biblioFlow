"""
PDF Processing Pipeline

Orchestrates the flow: PDF → DOI extraction → metadata lookup → file organization.
"""
import os
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from typing import Optional

from .extractor import extract_doi_from_pdf, extract_text_from_pdf
from .metadata import PaperMetadata, fetch_metadata, query_semantic_scholar
from .organizer import organize_file, generate_filename


class ProcessingResult:
    """Result of processing a single PDF."""
    
    def __init__(self, original_path: str):
        self.original_path = original_path
        self.filename = os.path.basename(original_path)
        self.metadata: Optional[PaperMetadata] = None
        self.new_path: Optional[str] = None
        self.error: Optional[str] = None
        self.success = False


class PDFProcessor(QThread):
    """
    Background thread for processing PDF files.
    
    Signals:
        processing_started: Emitted when processing begins (filename)
        metadata_found: Emitted when metadata is found (filename, metadata)
        confirmation_needed: Emitted when user confirmation is needed (result)
        processing_complete: Emitted when file is organized (old_path, new_path)
        processing_failed: Emitted on error (filename, error_message)
        batch_progress: Emitted for batch progress (current, total)
        batch_complete: Emitted when batch is done (results list)
    """
    
    processing_started = pyqtSignal(str)
    metadata_found = pyqtSignal(str, object)  # filename, PaperMetadata
    confirmation_needed = pyqtSignal(object)  # ProcessingResult
    processing_complete = pyqtSignal(str, str)  # old_path, new_path
    processing_failed = pyqtSignal(str, str)  # filename, error
    batch_progress = pyqtSignal(int, int)  # current, total
    batch_complete = pyqtSignal(list)  # list of ProcessingResult
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.files_to_process = []
        self.output_folder = ""
        self.naming_format = "default"
        self.auto_confirm = False
        self._results = []
    
    def set_files(self, file_paths: list):
        """Set files to process."""
        self.files_to_process = file_paths
    
    def set_output_folder(self, folder: str):
        """Set output folder for organized files."""
        self.output_folder = folder
    
    def set_naming_format(self, format_name: str):
        """Set naming format."""
        self.naming_format = format_name
    
    def set_auto_confirm(self, auto: bool):
        """Set whether to auto-confirm without user interaction."""
        self.auto_confirm = auto
    
    def run(self):
        """Process all queued files."""
        self._results = []
        total = len(self.files_to_process)
        
        for i, file_path in enumerate(self.files_to_process):
            result = self._process_single_file(file_path)
            self._results.append(result)
            self.batch_progress.emit(i + 1, total)
        
        self.batch_complete.emit(self._results)
    
    def _process_single_file(self, pdf_path: str) -> ProcessingResult:
        """Process a single PDF file."""
        result = ProcessingResult(pdf_path)
        filename = os.path.basename(pdf_path)
        
        self.processing_started.emit(filename)
        
        try:
            # Step 1: Extract DOI from PDF
            doi = extract_doi_from_pdf(pdf_path)
            
            # Step 2: Fetch metadata
            if doi:
                metadata = fetch_metadata(doi=doi)
            else:
                # Fallback: Try to extract title and search
                text = extract_text_from_pdf(pdf_path, max_pages=1)
                # Use first line as potential title
                lines = text.strip().split('\n')
                potential_title = lines[0] if lines else filename
                metadata = query_semantic_scholar(potential_title)
            
            if not metadata:
                result.error = "Could not find metadata for this paper"
                self.processing_failed.emit(filename, result.error)
                return result
            
            result.metadata = metadata
            self.metadata_found.emit(filename, metadata)
            
            # Step 3: Request confirmation or auto-confirm
            if not self.auto_confirm:
                self.confirmation_needed.emit(result)
                # Note: Actual file organization happens when user confirms
                # via confirm_result() method called from UI
            else:
                # Auto-confirm mode: organize immediately
                self._organize_file(result)
            
            return result
            
        except Exception as e:
            result.error = str(e)
            self.processing_failed.emit(filename, result.error)
            return result
    
    def confirm_result(self, result: ProcessingResult, custom_filename: Optional[str] = None):
        """
        Confirm and organize a file after user approval.
        
        Args:
            result: The ProcessingResult to confirm
            custom_filename: Optional custom filename override
        """
        if result.metadata:
            self._organize_file(result, custom_filename)
    
    def _organize_file(self, result: ProcessingResult, custom_filename: Optional[str] = None):
        """Organize a file based on its metadata."""
        if not result.metadata:
            return
        
        try:
            if custom_filename:
                # Use custom filename directly
                new_path = os.path.join(self.output_folder, custom_filename)
                os.makedirs(self.output_folder, exist_ok=True)
                import shutil
                shutil.move(result.original_path, new_path)
            else:
                new_path = organize_file(
                    result.original_path,
                    result.metadata,
                    self.output_folder,
                    self.naming_format
                )
            
            if new_path:
                result.new_path = new_path
                result.success = True
                self.processing_complete.emit(result.original_path, new_path)
            else:
                result.error = "Failed to organize file"
                self.processing_failed.emit(result.filename, result.error)
                
        except Exception as e:
            result.error = str(e)
            self.processing_failed.emit(result.filename, result.error)
