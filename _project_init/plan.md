# BiblioFlow Project Initialization Plan

Complete project scaffolding with GitHub Actions CI/CD, semantic versioning, and full auto-update for the PyQt6-based research PDF organizer.

---

## User Review Required

> [!IMPORTANT]
> **Auto-Update Implementation**: The auto-update will download and replace the `.exe` automatically. On Windows, this requires starting an updater script that waits for the app to close before replacing the executable.

> [!WARNING]
> **GitHub Secrets Required**: After this plan is executed, you'll need to manually add secrets in GitHub repo settings for the CI/CD to work properly (instructions provided in verification).

---

## Proposed Changes

### Version Management

#### [NEW] [version.py](file:///c:/Users/logan/Documents/biblioFlow/src/core/version.py)
Centralized version management:
```python
__version__ = "0.1.0"
APP_NAME = "BiblioFlow"
GITHUB_REPO = "logando-al/biblioFlow"
```

---

### Auto-Update System

#### [NEW] [updater.py](file:///c:/Users/logan/Documents/biblioFlow/src/core/updater.py)
Full auto-update module with:
- GitHub Releases API integration to check for new versions
- Download new `.exe` with progress callback
- Windows batch script generation for self-replacement
- Version comparison using semantic versioning

Key flow:
1. App checks GitHub Releases API on startup
2. Compares remote version vs local `__version__`
3. If update available → prompts user
4. Downloads new `.exe` to temp folder
5. Launches updater batch script → exits app
6. Batch script waits, replaces old exe, relaunches

---

### CI/CD Workflows

#### [NEW] [ci.yml](file:///c:/Users/logan/Documents/biblioFlow/.github/workflows/ci.yml)
Continuous Integration workflow:
- **Triggers**: Push to `main`, Pull Requests
- **Jobs**: Lint (flake8), Test (pytest), Build verification
- **Matrix**: Python 3.11 on Windows

#### [NEW] [release.yml](file:///c:/Users/logan/Documents/biblioFlow/.github/workflows/release.yml)
Release workflow:
- **Trigger**: Push tags matching `v*.*.*`
- **Jobs**:
  1. Build Windows `.exe` with PyInstaller
  2. Create GitHub Release
  3. Upload `.exe` as release asset
- **Auto-version**: Extracts version from tag, updates `version.py`

---

### Build Configuration

#### [NEW] [biblioflow.spec](file:///c:/Users/logan/Documents/biblioFlow/biblioflow.spec)
PyInstaller spec file for Windows build:
- One-file executable
- Includes all dependencies (PyQt6, qtawesome, etc.)
- Embeds version info for Windows

#### [NEW] [requirements.txt](file:///c:/Users/logan/Documents/biblioFlow/requirements.txt)
```
PyQt6>=6.6.0
qtawesome>=1.3.0
pypdf>=4.0.0
PyMuPDF>=1.23.0
requests>=2.31.0
beautifulsoup4>=4.12.0
packaging>=23.0
```

#### [NEW] [requirements-dev.txt](file:///c:/Users/logan/Documents/biblioFlow/requirements-dev.txt)
```
pytest>=8.0.0
flake8>=7.0.0
pyinstaller>=6.3.0
```

---

### Project Structure

#### [NEW] Project Scaffold
```
biblioflow/
├── .github/
│   └── workflows/
│       ├── ci.yml              # CI on push/PR
│       └── release.yml         # Build + release on tag
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── version.py          # Centralized version
│   │   ├── updater.py          # Auto-update logic
│   │   ├── extractor.py        # (stub)
│   │   ├── metadata.py         # (stub)
│   │   ├── organizer.py        # (stub)
│   │   └── bibtex.py           # (stub)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py              # Main window (stub)
│   │   ├── drop_zone.py        # (stub)
│   │   ├── library.py          # (stub)
│   │   ├── preview_card.py     # (stub)
│   │   └── settings.py         # (stub)
│   └── assets/
│       └── styles.qss          # Dark theme
├── data/
│   └── .gitkeep
├── tests/
│   └── test_version.py
├── main.py                     # Entry point
├── requirements.txt
├── requirements-dev.txt
├── biblioflow.spec             # PyInstaller config
├── .gitignore
└── README.md
```

---

### Repository Files

#### [NEW] [.gitignore](file:///c:/Users/logan/Documents/biblioFlow/.gitignore)
Standard Python + PyInstaller ignores:
- `__pycache__/`, `*.pyc`, `.venv/`
- `build/`, `dist/`, `*.spec` outputs
- IDE files

#### [NEW] [README.md](file:///c:/Users/logan/Documents/biblioFlow/README.md)
Project README with:
- Description from blueprint
- Installation instructions
- Development setup
- CI/CD badges

---

## Verification Plan

### Automated Tests
```bash
# Run after scaffolding
cd c:\Users\logan\Documents\biblioFlow
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
python -c "from src.core.version import __version__; print(__version__)"
```

### Manual Verification
1. **Git Push**: Initialize repo, push to GitHub
2. **CI Check**: Verify GitHub Actions runs on push
3. **Release Test**: Create tag `v0.1.0` → verify release workflow creates exe

### GitHub Setup (Manual Steps After Execution)
1. Go to repo Settings → Secrets and Variables → Actions
2. No secrets needed for public repo releases (uses `GITHUB_TOKEN`)
3. Enable Actions in repo if not already enabled

---

## Release Workflow

To create a new release:
```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers the release workflow which:
1. Updates `version.py` with tag version
2. Builds `.exe` with PyInstaller
3. Creates GitHub Release with changelog
4. Uploads `BiblioFlow-v0.1.0-win64.exe` as asset

The auto-updater in the app will detect this release and offer to update.
