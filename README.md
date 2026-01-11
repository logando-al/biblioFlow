# BiblioFlow

> An intelligent drop zone for researchers to auto-organize, rename, and cite research PDFs.

[![CI](https://github.com/logando-al/biblioFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/logando-al/biblioFlow/actions/workflows/ci.yml)
[![Release](https://github.com/logando-al/biblioFlow/actions/workflows/release.yml/badge.svg)](https://github.com/logando-al/biblioFlow/releases)

## Features

- **Drag & Drop** - Drop any research PDF onto the app
- **Auto-Extraction** - Scans for DOI, queries CrossRef/Semantic Scholar
- **Smart Rename** - Renames to `[Year] Author - Title.pdf`
- **Citation Formats** - Copy BibTeX, APA 7th, or IEEE to clipboard
- **RIS Export** - Export to Mendeley/Zotero/EndNote
- **Library View** - Searchable table of all organized papers
- **Watch Folder** - Auto-process new PDFs in a watched folder
- **Auto-Update** - Automatically updates to latest version

## Installation

### Windows

Download the latest `BiblioFlow-vX.X.X-win64.exe` from [Releases](https://github.com/logando-al/biblioFlow/releases).

### From Source

```bash
git clone https://github.com/logando-al/biblioFlow.git
cd biblioFlow
pip install -r requirements.txt
python main.py
```

## Development Setup

### 1. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/macOS)
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Run the App

```bash
python main.py
```

### 4. Run Tests & Linting

```bash
# Run tests
pytest tests/ -v

# Run linter
flake8 src/ --max-line-length=120
```

### 5. Build Executable

```bash
pyinstaller biblioflow.spec
```

The executable will be in `dist/BiblioFlow.exe`.

## Quick Setup Script (Windows)

```powershell
# Run this in PowerShell
.\setup.ps1
```

## Creating a Release

```bash
git tag v0.2.0
git push origin v0.2.0
```

This triggers the GitHub Actions release workflow which builds and uploads the Windows executable.

## License

MIT
