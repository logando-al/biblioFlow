"""
PDF Text and DOI Extractor

Extracts text from PDF files and finds DOI patterns.
"""
import re
from typing import Optional

# DOI pattern as specified in blueprint
DOI_PATTERN = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'


def extract_doi_from_text(text: str) -> Optional[str]:
    """
    Extract DOI from text using regex pattern.
    
    Args:
        text: Text content to search for DOI
        
    Returns:
        Optional[str]: Found DOI or None
    """
    match = re.search(DOI_PATTERN, text, re.IGNORECASE)
    if match:
        return match.group(0)
    return None


def extract_text_from_pdf(pdf_path: str, max_pages: int = 2) -> str:
    """
    Extract text from first N pages of a PDF.
    
    Args:
        pdf_path: Path to PDF file
        max_pages: Maximum number of pages to extract (default: 2)
        
    Returns:
        str: Extracted text content
    """
    try:
        import fitz  # PyMuPDF
        
        text_parts = []
        with fitz.open(pdf_path) as doc:
            for page_num in range(min(max_pages, len(doc))):
                page = doc[page_num]
                text_parts.append(page.get_text())
        
        return "\n".join(text_parts)
        
    except ImportError:
        # Fallback to pypdf
        try:
            from pypdf import PdfReader
            
            reader = PdfReader(pdf_path)
            text_parts = []
            for page_num in range(min(max_pages, len(reader.pages))):
                text_parts.append(reader.pages[page_num].extract_text())
            
            return "\n".join(text_parts)
            
        except Exception as e:
            print(f"PDF extraction failed: {e}")
            return ""
    
    except Exception as e:
        print(f"PDF extraction failed: {e}")
        return ""


def extract_doi_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract DOI from a PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Optional[str]: Found DOI or None
    """
    text = extract_text_from_pdf(pdf_path)
    return extract_doi_from_text(text)
