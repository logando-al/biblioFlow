"""BiblioFlow Core Module"""
from .version import __version__, APP_NAME, GITHUB_REPO
from .config import ConfigManager
from .library_store import LibraryStore

__all__ = ['__version__', 'APP_NAME', 'GITHUB_REPO', 'ConfigManager', 'LibraryStore']
