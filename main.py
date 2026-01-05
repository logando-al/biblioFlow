"""
BiblioFlow - Intelligent Research PDF Organizer

Entry point for the application.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import run_app


if __name__ == "__main__":
    run_app()
