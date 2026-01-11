"""
Library Store

Persists paper library to JSON file.
"""
import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from .metadata import PaperMetadata


class LibraryStore:
    """Manages persistent storage of paper library."""
    
    def __init__(self, path: str = "data/library.json"):
        self.path = path
        self._papers: List[Dict[str, Any]] = []
        self._load()
    
    def _load(self):
        """Load library from JSON file."""
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    self._papers = json.load(f)
        except Exception as e:
            print(f"Failed to load library: {e}")
            self._papers = []
    
    def _save(self):
        """Save library to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self._papers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save library: {e}")
    
    def add_paper(self, metadata: PaperMetadata, file_path: str) -> str:
        """
        Add a paper to the library.
        
        Args:
            metadata: Paper metadata
            file_path: Path to the organized PDF file
            
        Returns:
            str: Unique ID of the added paper
        """
        paper_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self._papers)}"
        
        paper = {
            "id": paper_id,
            "title": metadata.title,
            "authors": metadata.authors,
            "year": metadata.year,
            "journal": metadata.journal,
            "doi": metadata.doi,
            "abstract": metadata.abstract,
            "file_path": file_path,
            "added_at": datetime.now().isoformat(),
        }
        
        self._papers.append(paper)
        self._save()
        return paper_id
    
    def remove_paper(self, paper_id: str) -> bool:
        """Remove a paper by ID."""
        original_count = len(self._papers)
        self._papers = [p for p in self._papers if p.get("id") != paper_id]
        
        if len(self._papers) < original_count:
            self._save()
            return True
        return False
    
    def get_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get a paper by ID."""
        for paper in self._papers:
            if paper.get("id") == paper_id:
                return paper
        return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all papers in the library."""
        return self._papers.copy()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search papers by title, authors, or journal.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching papers
        """
        query = query.lower()
        results = []
        
        for paper in self._papers:
            if query in paper.get("title", "").lower():
                results.append(paper)
            elif any(query in author.lower() for author in paper.get("authors", [])):
                results.append(paper)
            elif query in paper.get("journal", "").lower():
                results.append(paper)
            elif query in paper.get("doi", "").lower():
                results.append(paper)
        
        return results
    
    def to_metadata(self, paper: Dict[str, Any]) -> PaperMetadata:
        """Convert stored paper dict back to PaperMetadata."""
        return PaperMetadata(
            title=paper.get("title", ""),
            authors=paper.get("authors", []),
            year=paper.get("year"),
            journal=paper.get("journal"),
            doi=paper.get("doi"),
            abstract=paper.get("abstract"),
        )
    
    def get_all_as_metadata(self) -> List[PaperMetadata]:
        """Get all papers as PaperMetadata objects."""
        return [self.to_metadata(p) for p in self._papers]
    
    @property
    def count(self) -> int:
        """Get total number of papers."""
        return len(self._papers)
