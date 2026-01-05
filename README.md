# BiblioFlow

> An intelligent drop zone for researchers to auto-organize, rename, and cite research PDFs.

[![CI](https://github.com/logando-al/biblioFlow/actions/workflows/ci.yml/badge.svg)](https://github.com/logando-al/biblioFlow/actions/workflows/ci.yml)
[![Release](https://github.com/logando-al/biblioFlow/actions/workflows/release.yml/badge.svg)](https://github.com/logando-al/biblioFlow/releases)

## Features

- **Drag & Drop** - Drop any research PDF onto the app
- **Auto-Extraction** - Scans for DOI, queries CrossRef/Semantic Scholar
- **Smart Rename** - Renames to `[Year] Author - Title.pdf`
- **BibTeX Generation** - One-click copy citation to clipboard
- **Library View** - Searchable table of all organized papers
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

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linter
flake8 src/

# Build executable
pyinstaller biblioflow.spec
```

## Creating a Release

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers the GitHub Actions release workflow which builds and uploads the Windows executable.

## License

MIT
