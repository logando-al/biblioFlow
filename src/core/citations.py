"""
Citation Generator

Generates citations in multiple formats: BibTeX, APA 7th, IEEE, and RIS.
"""
import re
from typing import List
from .metadata import PaperMetadata


def generate_bibtex_key(metadata: PaperMetadata) -> str:
    """
    Generate a BibTeX citation key.

    Format: AuthorYear (e.g., "Smith2024")
    """
    author = metadata.first_author if metadata.authors else "Unknown"
    author = re.sub(r'[^a-zA-Z]', '', author)
    year = str(metadata.year) if metadata.year else "0000"
    return f"{author}{year}"


def generate_bibtex(metadata: PaperMetadata) -> str:
    """
    Generate a BibTeX entry from metadata.

    Example:
        @article{Smith2024,
          title = {{Machine Learning for Research}},
          author = {Smith, John and Jones, Mary},
          year = {2024},
          journal = {Nature},
          doi = {10.1038/xxxxx},
        }
    """
    key = generate_bibtex_key(metadata)

    # Format authors for BibTeX (Last, First and Last, First)
    authors_bibtex = []
    for author in metadata.authors:
        parts = author.split()
        if len(parts) >= 2:
            authors_bibtex.append(f"{parts[-1]}, {' '.join(parts[:-1])}")
        else:
            authors_bibtex.append(author)

    author_string = " and ".join(authors_bibtex)

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


def _format_author_apa(name: str) -> str:
    """Format author name for APA style: Last, F. M."""
    parts = name.split()
    if len(parts) >= 2:
        last = parts[-1]
        initials = ". ".join([p[0].upper() for p in parts[:-1]]) + "."
        return f"{last}, {initials}"
    return name


def generate_apa7(metadata: PaperMetadata) -> str:
    """
    Generate APA 7th Edition citation.

    Example:
        Smith, J., & Jones, M. (2024). Machine learning for research.
        Nature, 12(3), 45-67. https://doi.org/10.1038/xxxxx
    """
    # Format authors
    if not metadata.authors:
        author_str = "Unknown"
    elif len(metadata.authors) == 1:
        author_str = _format_author_apa(metadata.authors[0])
    elif len(metadata.authors) == 2:
        author_str = f"{_format_author_apa(metadata.authors[0])}, & {_format_author_apa(metadata.authors[1])}"
    elif len(metadata.authors) <= 20:
        formatted = [_format_author_apa(a) for a in metadata.authors[:-1]]
        author_str = ", ".join(formatted) + f", & {_format_author_apa(metadata.authors[-1])}"
    else:
        # More than 20 authors: first 19, ..., last
        formatted = [_format_author_apa(a) for a in metadata.authors[:19]]
        author_str = ", ".join(formatted) + f", ... {_format_author_apa(metadata.authors[-1])}"

    # Year
    year = f"({metadata.year})" if metadata.year else "(n.d.)"

    # Title (sentence case, italicized for articles)
    title = metadata.title

    # Journal (italicized)
    journal = f"*{metadata.journal}*" if metadata.journal else ""

    # DOI
    doi = f"https://doi.org/{metadata.doi}" if metadata.doi else ""

    # Build citation
    parts = [f"{author_str} {year}. {title}."]
    if journal:
        parts.append(journal + ".")
    if doi:
        parts.append(doi)

    return " ".join(parts)


def _format_author_ieee(name: str) -> str:
    """Format author name for IEEE style: F. M. Last"""
    parts = name.split()
    if len(parts) >= 2:
        initials = " ".join([p[0].upper() + "." for p in parts[:-1]])
        return f"{initials} {parts[-1]}"
    return name


def generate_ieee(metadata: PaperMetadata) -> str:
    """
    Generate IEEE citation.

    Example:
        J. Smith and M. Jones, "Machine learning for research,"
        Nature, vol. 12, no. 3, pp. 45-67, 2024.
    """
    # Format authors
    if not metadata.authors:
        author_str = "Unknown"
    elif len(metadata.authors) == 1:
        author_str = _format_author_ieee(metadata.authors[0])
    elif len(metadata.authors) == 2:
        author_str = f"{_format_author_ieee(metadata.authors[0])} and {_format_author_ieee(metadata.authors[1])}"
    else:
        formatted = [_format_author_ieee(a) for a in metadata.authors[:-1]]
        author_str = ", ".join(formatted) + f", and {_format_author_ieee(metadata.authors[-1])}"

    # Title in quotes
    title = f'"{metadata.title},"'

    # Journal italicized
    journal = f"*{metadata.journal}*," if metadata.journal else ""

    # Year
    year = str(metadata.year) if metadata.year else "n.d."

    # Build citation
    parts = [author_str, title]
    if journal:
        parts.append(journal)
    parts.append(year + ".")

    return " ".join(parts)


def generate_ris(metadata: PaperMetadata) -> str:
    """
    Generate RIS format for reference managers (Mendeley, Zotero, EndNote).

    Example:
        TY  - JOUR
        TI  - Machine learning for research
        AU  - Smith, John
        AU  - Jones, Mary
        PY  - 2024
        JO  - Nature
        DO  - 10.1038/xxxxx
        ER  -
    """
    lines = ["TY  - JOUR"]

    lines.append(f"TI  - {metadata.title}")

    for author in metadata.authors:
        # RIS format: Last, First
        parts = author.split()
        if len(parts) >= 2:
            ris_author = f"{parts[-1]}, {' '.join(parts[:-1])}"
        else:
            ris_author = author
        lines.append(f"AU  - {ris_author}")

    if metadata.year:
        lines.append(f"PY  - {metadata.year}")

    if metadata.journal:
        lines.append(f"JO  - {metadata.journal}")

    if metadata.doi:
        lines.append(f"DO  - {metadata.doi}")

    if metadata.abstract:
        lines.append(f"AB  - {metadata.abstract}")

    lines.append("ER  -")

    return "\n".join(lines)


def generate_ris_batch(papers: List[PaperMetadata]) -> str:
    """
    Generate RIS format for multiple papers.

    Each paper is separated by a blank line.
    """
    ris_entries = [generate_ris(paper) for paper in papers]
    return "\n\n".join(ris_entries)


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.

    Args:
        text: Text to copy

    Returns:
        bool: True if successful
    """
    try:
        from PyQt6.QtWidgets import QApplication

        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        return True

    except Exception as e:
        print(f"Clipboard copy failed: {e}")
        return False
