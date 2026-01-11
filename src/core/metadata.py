"""
Metadata API Integration

Queries CrossRef and Semantic Scholar APIs for paper metadata.
"""
import requests
from typing import Optional
from dataclasses import dataclass


@dataclass
class PaperMetadata:
    """Represents metadata for a research paper."""
    title: str
    authors: list[str]
    year: Optional[int]
    journal: Optional[str]
    doi: Optional[str]
    abstract: Optional[str] = None

    @property
    def first_author(self) -> str:
        """Get first author's last name."""
        if self.authors:
            # Try to extract last name
            name = self.authors[0]
            parts = name.split()
            return parts[-1] if parts else name
        return "Unknown"

    @property
    def author_string(self) -> str:
        """Get formatted author string."""
        if not self.authors:
            return "Unknown"
        if len(self.authors) == 1:
            return self.first_author
        elif len(self.authors) == 2:
            return f"{self.authors[0].split()[-1]} & {self.authors[1].split()[-1]}"
        else:
            return f"{self.first_author} et al."


def query_crossref(doi: str) -> Optional[PaperMetadata]:
    """
    Query CrossRef API for paper metadata by DOI.

    Args:
        doi: DOI string (e.g., "10.1038/s41586-024-07051-4")

    Returns:
        Optional[PaperMetadata]: Metadata if found, None otherwise
    """
    url = f"https://api.crossref.org/works/{doi}"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/json"},
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        message = data.get("message", {})

        # Extract authors
        authors = []
        for author in message.get("author", []):
            given = author.get("given", "")
            family = author.get("family", "")
            if family:
                authors.append(f"{given} {family}".strip())

        # Extract year
        year = None
        if "published-print" in message:
            date_parts = message["published-print"].get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
        elif "published-online" in message:
            date_parts = message["published-online"].get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

        # Extract title
        title_list = message.get("title", [])
        title = title_list[0] if title_list else "Untitled"

        # Extract journal
        container = message.get("container-title", [])
        journal = container[0] if container else None

        return PaperMetadata(
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            doi=doi,
            abstract=message.get("abstract")
        )

    except Exception as e:
        print(f"CrossRef query failed: {e}")
        return None


def query_semantic_scholar(title: str) -> Optional[PaperMetadata]:
    """
    Query Semantic Scholar API by title (fallback when no DOI).

    Args:
        title: Paper title to search

    Returns:
        Optional[PaperMetadata]: Metadata if found, None otherwise
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    try:
        response = requests.get(
            url,
            params={
                "query": title,
                "limit": 1,
                "fields": "title,authors,year,venue,externalIds,abstract"
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        papers = data.get("data", [])
        if not papers:
            return None

        paper = papers[0]

        # Extract authors
        authors = [a.get("name", "") for a in paper.get("authors", [])]

        # Extract DOI
        external_ids = paper.get("externalIds", {})
        doi = external_ids.get("DOI")

        return PaperMetadata(
            title=paper.get("title", "Untitled"),
            authors=authors,
            year=paper.get("year"),
            journal=paper.get("venue"),
            doi=doi,
            abstract=paper.get("abstract")
        )

    except Exception as e:
        print(f"Semantic Scholar query failed: {e}")
        return None


def fetch_metadata(doi: Optional[str] = None, title: Optional[str] = None) -> Optional[PaperMetadata]:
    """
    Fetch metadata using DOI (preferred) or title search (fallback).

    Args:
        doi: DOI string if available
        title: Paper title for fallback search

    Returns:
        Optional[PaperMetadata]: Metadata if found, None otherwise
    """
    if doi:
        metadata = query_crossref(doi)
        if metadata:
            return metadata

    if title:
        return query_semantic_scholar(title)

    return None
