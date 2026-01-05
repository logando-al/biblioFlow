"""
Tests for version module.
"""
import pytest
from src.core.version import __version__, APP_NAME, GITHUB_REPO


def test_version_format():
    """Test that version follows semantic versioning."""
    parts = __version__.split('.')
    assert len(parts) == 3, "Version should have 3 parts (major.minor.patch)"
    for part in parts:
        assert part.isdigit(), f"Version part '{part}' should be numeric"


def test_app_name():
    """Test app name is set."""
    assert APP_NAME == "BiblioFlow"


def test_github_repo():
    """Test GitHub repo is set."""
    assert GITHUB_REPO == "logando-al/biblioFlow"
    assert "/" in GITHUB_REPO, "Repo should be in format owner/repo"
