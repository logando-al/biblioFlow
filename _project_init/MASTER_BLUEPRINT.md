# Project: BiblioFlow
> An intelligent drop zone for researchers to auto-organize, rename, and cite research PDFs.
---
## 1. The Strategy
| Aspect | Detail |
|--------|--------|
| **Pitch** | Drag any research PDF → auto-extract metadata via DOI/Google Scholar → rename to `[Year] Author - Title.pdf` → copy BibTeX with one click. |
| **Target User** | Master's/PhD students, academic researchers, anyone managing a library of papers. |
| **Monetization** | Portfolio Flex (Primary) / Open Source / Freemium with cloud sync. |
| **Portfolio Flex** | Demonstrates API integration, web scraping, file I/O, regex parsing, and clean UI design. |
---
## 2. Tech Architecture
### Stack
| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **GUI Framework** | PyQt6 |
| **Icons** | `QtAwesome` (Font Awesome icons for Qt) |
| **PDF Parsing** | `pypdf` / `PyMuPDF` (fitz) |
| **Web Scraping** | `BeautifulSoup4`, `requests` |
| **Metadata APIs** | CrossRef API (DOI lookup), Semantic Scholar, OpenAlex |
| **RegEx** | `re` module (DOI extraction) |
| **Packaging** | PyInstaller (→ `.exe`) |
### Core Modules
```
┌─────────────────────────────────────────────────────────────────┐
│                         BIBLIOFLOW                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   DROP ZONE  │───▶│   EXTRACTOR  │───▶│    ORGANIZER     │  │
│  │              │    │              │    │                  │  │
│  │ • Drag PDF   │    │ • Scan PDF   │    │ • Rename File    │  │
│  │ • Watch Dir  │    │ • Find DOI   │    │ • Move to Folder │  │
│  │              │    │ • Query API  │    │ • Store BibTeX   │  │
│  └──────────────┘    └──────────────┘    └──────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                      LIBRARY VIEW                         │  │
│  │  • Search & Filter  • Right-click → Copy BibTeX          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
### Data Flow
1. **Input**: User drags `paper_final_v2.pdf` into drop zone
2. **Extract**: App scans first 2 pages for DOI pattern (`10.xxxx/xxxxx`)
3. **Query**: If DOI found → CrossRef API → Get title, authors, year, journal
4. **Fallback**: If no DOI → Extract title text → Query Semantic Scholar
5. **Rename**: `paper_final_v2.pdf` → `[2024] Smith, J. - Machine Learning for X.pdf`
6. **Move**: File moved to organized library folder
7. **Store**: BibTeX citation stored in local JSON/SQLite for quick retrieval
### DOI Regex Pattern
```python
DOI_PATTERN = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
```
---
## 3. UX Vision
### Vibe
> **Modern • Academic • Refined**
> [!IMPORTANT]
> **Strictly NO emoji in the UI.** All icons must use **QtAwesome** (Font Awesome icons for Qt).
### Icon Examples (QtAwesome)
```python
import qtawesome as qta
# Common icons
qta.icon('fa5s.file-pdf')       # PDF file
qta.icon('fa5s.search')         # Search
qta.icon('fa5s.check')          # Success/Confirm
qta.icon('fa5s.times')          # Cancel/Close
qta.icon('fa5s.edit')           # Edit
qta.icon('fa5s.copy')           # Copy to clipboard
qta.icon('fa5s.folder-open')    # Open folder
qta.icon('fa5s.cog')            # Settings
qta.icon('fa5s.book')           # Library
qta.icon('fa5s.download')       # Download/Import
```
### Color Palette
| Element | Color |
|---------|-------|
| **Background** | `#0D0D0D` (Deep Black) |
| **Surface** | `#1A1A1A` (Card Background) |
| **Text Primary** | `#FFFFFF` (Pure White) |
| **Text Secondary** | `#A0A0A0` (Muted Gray) |
| **Accent** | `#1E3A5F` (Navy Blue) |
| **Accent Glow** | `#3B82F6` (Electric Blue - on hover) |
| **Success** | `#22C55E` (Green) |
| **Error** | `#EF4444` (Red) |
### Hover Effect (CSS/QSS)
```css
QPushButton {
    background-color: #1E3A5F;
    border: 1px solid #3B82F6;
    border-radius: 6px;
    color: white;
}
QPushButton:hover {
    background-color: #2563EB;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.6);  /* Glow effect */
}
```
### Key Views
| View | Purpose |
|------|---------|
| **Drop Zone** | Large drag-and-drop area with animated border pulse |
| **Processing Queue** | Shows files being processed with status indicators |
| **Library** | Searchable table of all organized papers |
| **Settings** | Output folder, naming format, API keys |
### Naming Format Options
- `[Year] Author - Title.pdf` (Default)
- `Author_Year_Title.pdf`
- `Title (Year).pdf`
- Custom pattern with tokens: `{year}`, `{author}`, `{title}`, `{journal}`
---
## 4. User Story (Happy Path)
```
1. User launches BiblioFlow
2. Drags "downloaded_paper (1).pdf" onto the drop zone
3. App shows processing spinner with "Extracting metadata..."
4. DOI found: 10.1038/s41586-024-07051-4
5. App queries CrossRef API → retrieves metadata
6. Preview card appears:
   ┌─────────────────────────────────────────────┐
   │  [file-pdf] Original: downloaded_paper.pdf  │
   │  [magic]    New Name: [2024] Chen, L. - ... │
   │  [book]     Journal: Nature                 │
   │  [Confirm]  [Edit]  [Cancel]                │
   └─────────────────────────────────────────────┘
7. User clicks Confirm
8. File renamed and moved to ~/Research/Papers/
9. Later: User right-clicks in Library → "Copy BibTeX" → Pastes into LaTeX
```
---
## 5. Development Phases
### Phase 1: Core Engine (MVP)
- [ ] PyQt6 window with drag-and-drop zone
- [ ] PDF text extraction (first 2 pages)
- [ ] DOI regex detection
- [ ] CrossRef API integration
- [ ] File rename + move logic
- [ ] Basic Library view (table)
### Phase 2: Smart Features
- [ ] Fallback: Title-based search (Semantic Scholar)
- [ ] BibTeX generation + clipboard copy
- [ ] Settings panel (output folder, naming format)
- [ ] Watch folder mode (auto-process new files)
### Phase 3: Polish & Academic Aesthetic
- [ ] Navy blue glow hover effects
- [ ] Animated drop zone border
- [ ] Dark mode refinement
- [ ] System tray integration
- [ ] PyInstaller packaging
---
## 6. File Structure (Proposed)
```
biblioflow/
├── main.py                    # Entry point
├── requirements.txt           # PyQt6, pypdf, requests, beautifulsoup4
├── src/
│   ├── core/
│   │   ├── extractor.py       # PDF text + DOI extraction
│   │   ├── metadata.py        # API queries (CrossRef, Semantic Scholar)
│   │   ├── organizer.py       # Rename + move logic
│   │   └── bibtex.py          # BibTeX generation
│   ├── ui/
│   │   ├── app.py             # Main window
│   │   ├── drop_zone.py       # Drag-and-drop widget
│   │   ├── library.py         # Library table view
│   │   ├── preview_card.py    # Metadata confirmation dialog
│   │   └── settings.py        # Settings panel
│   └── assets/
│       ├── styles.qss         # Dark theme + navy glow
│       └── icons/             # App icons
├── data/
│   └── library.json           # Local paper database
└── build.spec                 # PyInstaller config
```
---
## 7. API Reference
### CrossRef (Free, No API Key Required)
```
GET https://api.crossref.org/works/{DOI}
```
Returns: Title, Authors, Year, Journal, Abstract, BibTeX
### Semantic Scholar (Free, Optional API Key)
```
GET https://api.semanticscholar.org/graph/v1/paper/search?query={title}
```
Fallback when no DOI is found.
---
## 8. Next Steps
1. **Approve this Blueprint** — Let me know if the vision is correct
2. **Scaffold the Project** — Create folder structure + dependencies
3. **Build Phase 1** — Drop zone + DOI extraction + CrossRef integration
4. **Iterate** — Add library view, BibTeX, and polish
---
**Ready to build your research assistant?** 📚✨