"""
BibTeX Generator

Generates BibTeX citations from paper metadata.
"""
import re
from typing import Optional
from .metadata import PaperMetadata


def generate_bibtex_key(metadata: PaperMetadata) -> str:
    """
    Generate a BibTeX citation key.
    
    Format: AuthorYear (e.g., "Smith2024")
    
    Args:
        metadata: Paper metadata
        
    Returns:
        str: BibTeX citation key
    """
    author = metadata.first_author if metadata.authors else "Unknown"
    # Remove special characters
    author = re.sub(r'[^a-zA-Z]', '', author)
    year = str(metadata.year) if metadata.year else "0000"
    
    return f"{author}{year}"


def generate_bibtex(metadata: PaperMetadata) -> str:
    """
    Generate a BibTeX entry from metadata.
    
    Args:
        metadata: Paper metadata
        
    Returns:
        str: BibTeX formatted citation
    """
    key = generate_bibtex_key(metadata)
    
    # Format authors for BibTeX (Last, First and Last, First)
    authors_bibtex = []
    for author in metadata.authors:
        parts = author.split()
        if len(parts) >= 2:
            # Assume "First Last" format
            authors_bibtex.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
        else:
            authors_bibtex.append(author)
    
    author_string = " and ".join(authors_bibtex)
    
    # Build BibTeX entry
    lines = [f"@article{{{key},"]
    
    lines.append(f'  title = {{{{{metadata.title}}}}},')
    
    if author_string:
        lines.append(f'  author = {{{author_string}}},')
    
    if metadata.year:
        lines.append(f'  year = {{{metadata.year}}},')
    
    if metadata.journal:
        lines.append(f'  journal = {{{metadata.journal}}},')
    
    if metadata.doi:
        lines.append(f'  doi = {{{metadata.doi}}},')
    
    lines.append("}")
    
    return "\n".join(lines)


def copy_bibtex_to_clipboard(bibtex: str) -> bool:
    """
    Copy BibTeX string to system clipboard.
    
    Args:
        bibtex: BibTeX string to copy
        
    Returns:
        bool: True if successful
    """
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QMimeData
        
        clipboard = QApplication.clipboard()
        clipboard.setText(bibtex)
        return True
        
    except Exception as e:
        print(f"Clipboard copy failed: {e}")
        return False
