# AI Agent Implementation Notes: HuG

**Purpose:** Guidelines for AI agents implementing the HuG specification  
**Version:** 1.0  
**Date:** December 2024

---

## 1. Document Overview

This project consists of three specification documents:

| Document | Purpose | Read When |
|----------|---------|-----------|
| `HuG-01-TECHNICAL-SPECIFICATION.md` | Requirements, features, UI specs | Understanding what to build |
| `HuG-02-IMPLEMENTATION-GUIDE.md` | Architecture, code structure, platform details | Writing code |
| `HuG-03-JSON-SCHEMA-REFERENCE.md` | Data format, examples, validation | Working with snippet files |

**Read order:** 01 → 02 → 03

---

## 2. Implementation Priorities

### 2.1 Critical Path (Must Work First)

1. **Snippet loading** - Parse JSON libraries into memory
2. **Text insertion** - Clipboard + paste mechanism
3. **System tray** - Icon with working context menu
4. **Basic menu** - Snippets accessible via tray menu

Get these four working before anything else. This creates a minimally functional application.

### 2.2 Second Priority

5. **Configuration** - Load/save config.json
6. **Global hotkey** - Summon palette shortcut
7. **Floating palette** - Basic window with tree view
8. **Filter/search** - Narrow snippet list

### 2.3 Third Priority

9. **Settings dialog** - User preferences UI
10. **Preview pane** - Show snippet content before insertion
11. **File watcher** - Auto-reload on library changes
12. **Polish** - Themes, keyboard navigation, edge cases

---

## 3. Common Implementation Pitfalls

### 3.1 Cross-Platform Keyboard Issues

**Problem:** Paste simulation behaves differently across platforms.

**Solutions:**
- Always use clipboard + paste, never simulate typing
- Add small delay (50-100ms) between clipboard set and paste
- Use Qt's `QClipboard` rather than third-party clipboard libraries
- Test on each platform—don't assume Linux behavior matches Windows

### 3.2 System Tray Availability

**Problem:** Not all Linux desktop environments support system tray.

**Solutions:**
- Check `QSystemTrayIcon.isSystemTrayAvailable()` at startup
- Provide fallback: small always-visible window if tray unavailable
- Document which desktop environments are supported
- GNOME users need AppIndicator extension

### 3.3 Global Hotkey Conflicts

**Problem:** Requested hotkey may already be in use.

**Solutions:**
- Catch registration failures gracefully
- Inform user if hotkey is unavailable
- Continue running without hotkey (tray still works)
- Provide UI to change hotkey if registration fails

### 3.4 JSON Encoding Issues

**Problem:** Snippet content may contain special characters.

**Solutions:**
- Always read/write JSON with explicit UTF-8 encoding
- Handle BOM (byte order mark) gracefully
- Validate JSON before attempting to parse
- Provide clear error messages for malformed files

### 3.5 Wayland Considerations

**Problem:** Wayland restricts global keyboard hooks and clipboard access.

**Solutions:**
- Detect Wayland vs X11 at runtime
- For Wayland, may need portal APIs or fallback mechanisms
- Consider `wl-clipboard` as clipboard fallback
- Document Wayland limitations clearly

---

## 4. Testing Checkpoints

### 4.1 Checkpoint 1: Core Function

Run this test before proceeding to UI work:

```python
# Manual test script
from hug.models.library import LibraryManager
from hug.services.inserter import TextInserter
from pathlib import Path

# Load snippets
mgr = LibraryManager([Path("./snippets")])
mgr.load_all()
print(f"Loaded {len(mgr.get_all_snippets())} snippets")

# Find a snippet
snippet = mgr.search("for loop")[0]
print(f"Found: {snippet.name}")

# Insert it (open a text editor first!)
import time
time.sleep(3)  # Time to focus text editor
inserter = TextInserter()
inserter.insert(snippet.content)
```

### 4.2 Checkpoint 2: Tray Integration

- [ ] Tray icon appears
- [ ] Right-click shows menu
- [ ] Menu contains loaded snippets
- [ ] Clicking snippet inserts text
- [ ] "Quit" menu item exits cleanly

### 4.3 Checkpoint 3: Palette Function

- [ ] Hotkey summons palette
- [ ] Palette shows snippet tree
- [ ] Filter narrows results
- [ ] Double-click inserts snippet
- [ ] Escape closes palette
- [ ] Palette hides on focus loss (if configured)

### 4.4 Checkpoint 4: Cross-Platform

Test on each target platform:

- [ ] Windows 10/11
- [ ] Linux (Ubuntu with GNOME, and one other DE)
- [ ] macOS (if available)

---

## 5. Code Quality Guidelines

### 5.1 Type Hints

Use Python type hints throughout:

```python
# Good
def load_library(path: Path) -> SnippetLibrary:
    ...

# Avoid
def load_library(path):
    ...
```

### 5.2 Error Handling

Never let the application crash from user data issues:

```python
# Good
def load_library(path: Path) -> SnippetLibrary | None:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return SnippetLibrary.from_dict(data)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.error(f"Failed to load {path}: {e}")
        return None
```

### 5.3 Logging

Log meaningful events, not spam:

```python
# Good
logger.info(f"Loaded {len(snippets)} snippets from {path.name}")
logger.warning(f"Hotkey {hotkey} already in use, registration failed")
logger.error(f"Failed to insert snippet: {e}")
```

---

## 6. Incremental Build Steps

For AI agents building this project, follow these steps in order:

### Step 1: Project Skeleton
Create directory structure and `pyproject.toml`. Verify `pip install -e .` works.

### Step 2: Data Models
Implement `Snippet` and `SnippetLibrary` dataclasses. Write unit tests. Verify JSON parsing with sample files.

### Step 3: Configuration
Implement `Config` class with loading/saving. Create default config. Test persistence.

### Step 4: Text Inserter
Implement clipboard-based insertion. Test manually in various applications.

### Step 5: Minimal Tray App
Create `QApplication` with `QSystemTrayIcon`. Static menu with one test snippet. Verify insertion works end-to-end.

### Step 6: Dynamic Menu
Build menu from loaded libraries. Category submenus. Full snippet selection flow.

### Step 7: Hotkey Service
Implement global hotkey registration. Connect to palette toggle.

### Step 8: Floating Palette
Create palette window. Tree view population. Filter functionality. Snippet selection.

### Step 9: Integration
Connect all components. Hotkey shows palette. Selection inserts text. Escape hides palette.

### Step 10: Settings
Settings dialog UI. Connect to config. Persist changes.

### Step 11: Polish
File watcher. Themes. Keyboard navigation. Error handling review.

### Step 12: Packaging
PyInstaller configuration. Platform-specific builds. Test packaged application.

---

## 7. Sample Starter Code

### 7.1 Entry Point (`__main__.py`)

```python
"""Application entry point."""
import sys
from hug.app import HugApp


def main() -> int:
    app = HugApp(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
```

### 7.2 Snippet Model (`models/snippet.py`)

```python
"""Snippet data model."""
from dataclasses import dataclass, field


@dataclass
class Snippet:
    """A text snippet for insertion."""
    
    id: str
    name: str
    content: str
    description: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    library_name: str = ""
    language: str = ""
    
    def matches_filter(self, query: str) -> bool:
        """Check if snippet matches a search query."""
        query = query.lower()
        return (
            query in self.name.lower()
            or query in self.description.lower()
            or any(query in tag.lower() for tag in self.tags)
        )
    
    @classmethod
    def from_dict(cls, data: dict, library_name: str = "", language: str = "") -> "Snippet":
        """Create Snippet from dictionary (parsed JSON)."""
        return cls(
            id=data["id"],
            name=data["name"],
            content=data["content"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            tags=data.get("tags", []),
            library_name=library_name,
            language=language,
        )
```

### 7.3 Library Model (`models/library.py`)

```python
"""Snippet library loading and management."""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from .snippet import Snippet

logger = logging.getLogger(__name__)


@dataclass
class SnippetLibrary:
    """A collection of related snippets."""
    
    name: str
    snippets: list[Snippet]
    description: str = ""
    language: str = ""
    file_extensions: list[str] = field(default_factory=list)
    version: str = "1.0"
    author: str = ""
    source_path: Path | None = None
    
    @classmethod
    def from_json(cls, path: Path) -> "SnippetLibrary | None":
        """Load library from JSON file. Returns None on error."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            language = data.get("language", "")
            library_name = data["name"]
            
            snippets = [
                Snippet.from_dict(s, library_name=library_name, language=language)
                for s in data.get("snippets", [])
            ]
            
            return cls(
                name=library_name,
                snippets=snippets,
                description=data.get("description", ""),
                language=language,
                file_extensions=data.get("file_extensions", []),
                version=data.get("version", "1.0"),
                author=data.get("author", ""),
                source_path=path,
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to load library from {path}: {e}")
            return None


class LibraryManager:
    """Manages loading and searching snippet libraries."""
    
    def __init__(self, library_paths: list[Path]):
        self.library_paths = library_paths
        self.libraries: list[SnippetLibrary] = []
    
    def load_all(self) -> None:
        """Scan library paths and load all JSON files."""
        self.libraries.clear()
        
        for base_path in self.library_paths:
            if not base_path.exists():
                logger.warning(f"Library path does not exist: {base_path}")
                continue
            
            for json_file in base_path.rglob("*.json"):
                library = SnippetLibrary.from_json(json_file)
                if library:
                    self.libraries.append(library)
                    logger.info(f"Loaded {len(library.snippets)} snippets from {json_file.name}")
    
    def get_all_snippets(self) -> list[Snippet]:
        """Return flat list of all snippets."""
        return [s for lib in self.libraries for s in lib.snippets]
    
    def search(self, query: str) -> list[Snippet]:
        """Search all snippets by query string."""
        return [s for s in self.get_all_snippets() if s.matches_filter(query)]
```

---

## 8. Success Criteria

The implementation is complete when:

1. **Functional:** User can browse and insert snippets via tray menu
2. **Usable:** Global hotkey summons searchable palette
3. **Configurable:** Settings persist across sessions
4. **Stable:** No crashes from malformed snippet files
5. **Cross-platform:** Works on Windows and Linux (macOS if possible)
6. **Documented:** README explains installation and usage
7. **Packageable:** PyInstaller creates working executable

---

## 9. Reference Links

- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [pynput Documentation](https://pynput.readthedocs.io/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
