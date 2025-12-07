# Implementation Guide: HuG - Cross-Platform Snippet Manager

**Version:** 1.0  
**Status:** Draft  
**Date:** December 2024

---

## 1. Technology Stack

### 1.1 Core Technologies

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Language | Python 3.10+ | Cross-platform, readable, strong library ecosystem |
| GUI Framework | PySide6 (Qt 6) | Native look, excellent tray/system integration, cross-platform |
| Keyboard Simulation | pynput | Cross-platform keyboard/mouse control |
| Configuration | JSON (stdlib) | Human-readable, no external dependencies |
| Packaging | PyInstaller | Single executable distribution |

### 1.2 Dependencies

```
# requirements.txt
PySide6>=6.5.0
pynput>=1.7.6
```

### 1.3 Development Dependencies

```
# requirements-dev.txt
pytest>=7.0.0
pytest-qt>=4.2.0
black>=23.0.0
mypy>=1.0.0
pyinstaller>=5.0.0
```

---

## 2. Project Structure

```
hug/
├── src/
│   └── hug/
│       ├── __init__.py
│       ├── __main__.py           # Entry point
│       ├── app.py                # Application class, lifecycle management
│       ├── config.py             # Configuration loading/saving
│       ├── models/
│       │   ├── __init__.py
│       │   ├── snippet.py        # Snippet dataclass
│       │   └── library.py        # Library loading and management
│       ├── services/
│       │   ├── __init__.py
│       │   ├── hotkey.py         # Global hotkey registration
│       │   ├── inserter.py       # Clipboard/paste text insertion
│       │   └── watcher.py        # File system watcher for library changes
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── tray.py           # System tray icon and menu
│       │   ├── palette.py        # Floating palette window
│       │   ├── settings.py       # Settings dialog
│       │   └── widgets/
│       │       ├── __init__.py
│       │       ├── snippet_tree.py    # Tree view widget
│       │       └── preview_pane.py    # Snippet preview widget
│       └── resources/
│           ├── icons/
│           │   ├── hug.png
│           │   ├── hug.ico
│           │   └── hug.icns
│           └── themes/
│               ├── light.qss
│               └── dark.qss
├── snippets/                     # Default snippet libraries
│   ├── general/
│   │   └── common.json
│   └── code/
│       ├── python.json
│       ├── ruby.json
│       └── javascript.json
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_library.py
│   ├── test_inserter.py
│   └── test_models.py
├── scripts/
│   ├── build_windows.py
│   ├── build_linux.py
│   └── build_macos.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── LICENSE
```

---

## 3. Module Specifications

### 3.1 Entry Point (`__main__.py`)

```python
"""Application entry point."""
import sys
from hug.app import HugApp

def main():
    app = HugApp(sys.argv)
    sys.exit(app.run())

if __name__ == "__main__":
    main()
```

### 3.2 Application Class (`app.py`)

**Responsibilities:**
- Initialize Qt application
- Load configuration
- Create and connect all components
- Handle application lifecycle

**Key Methods:**

```python
class HugApp:
    def __init__(self, argv: list[str]):
        """Initialize application, load config, create components."""
        
    def run(self) -> int:
        """Start event loop, return exit code."""
        
    def reload_snippets(self) -> None:
        """Reload all snippet libraries from disk."""
        
    def show_palette(self) -> None:
        """Show/raise floating palette window."""
        
    def hide_palette(self) -> None:
        """Hide floating palette window."""
        
    def insert_snippet(self, snippet: Snippet) -> None:
        """Insert snippet at current cursor position."""
        
    def quit(self) -> None:
        """Clean shutdown: unregister hotkeys, save state, exit."""
```

### 3.3 Configuration (`config.py`)

**Responsibilities:**
- Load configuration from JSON file
- Provide defaults for missing values
- Save configuration changes
- Resolve platform-specific paths

**Key Classes:**

```python
@dataclass
class HotkeyConfig:
    summon_palette: str = "Ctrl+Shift+Space"
    
@dataclass  
class PaletteConfig:
    enabled: bool = True
    position: str = "remember"  # "remember", "cursor", "fixed"
    width: int = 350
    height: int = 450
    x: int | None = None  # For "fixed" or remembered position
    y: int | None = None
    hide_on_focus_loss: bool = True
    hide_on_selection: bool = True
    show_preview: bool = True

@dataclass
class ClipboardConfig:
    restore_previous: bool = True
    restore_delay_ms: int = 100

@dataclass
class AppearanceConfig:
    theme: str = "system"  # "system", "light", "dark"
    font_family: str = "monospace"
    font_size: int = 12

@dataclass
class StartupConfig:
    start_minimized: bool = True
    start_on_login: bool = False

@dataclass
class Config:
    version: str = "1.0"
    hotkey: HotkeyConfig
    palette: PaletteConfig
    clipboard: ClipboardConfig
    appearance: AppearanceConfig
    startup: StartupConfig
    library_paths: list[str]
    
    @classmethod
    def load(cls, path: Path) -> "Config":
        """Load config from JSON file, applying defaults."""
        
    def save(self, path: Path) -> None:
        """Save current config to JSON file."""
        
    @staticmethod
    def get_default_paths() -> list[str]:
        """Return platform-appropriate default library paths."""
```

### 3.4 Models

#### 3.4.1 Snippet (`models/snippet.py`)

```python
@dataclass
class Snippet:
    id: str
    name: str
    content: str
    description: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)
    
    # Back-reference to containing library (set during loading)
    library_name: str = ""
    language: str = ""
    
    def matches_filter(self, query: str) -> bool:
        """Check if snippet matches search query."""
        query = query.lower()
        return (
            query in self.name.lower() or
            query in self.description.lower() or
            any(query in tag.lower() for tag in self.tags)
        )
```

#### 3.4.2 Library (`models/library.py`)

```python
@dataclass
class SnippetLibrary:
    name: str
    snippets: list[Snippet]
    description: str = ""
    language: str = ""
    file_extensions: list[str] = field(default_factory=list)
    version: str = "1.0"
    author: str = ""
    source_path: Path | None = None
    
    @classmethod
    def from_json(cls, path: Path) -> "SnippetLibrary":
        """Load library from JSON file."""
        
    def get_categories(self) -> list[str]:
        """Return sorted list of unique categories."""
        
    def get_snippets_by_category(self, category: str) -> list[Snippet]:
        """Return snippets in given category."""


class LibraryManager:
    def __init__(self, library_paths: list[Path]):
        self.library_paths = library_paths
        self.libraries: dict[str, SnippetLibrary] = {}
        self.general_libraries: list[SnippetLibrary] = []
        self.code_libraries: dict[str, SnippetLibrary] = {}  # keyed by language
        
    def load_all(self) -> None:
        """Scan library paths and load all JSON files."""
        
    def reload(self) -> None:
        """Clear and reload all libraries."""
        
    def get_all_snippets(self) -> list[Snippet]:
        """Return flat list of all snippets."""
        
    def search(self, query: str) -> list[Snippet]:
        """Search all snippets by query string."""
```

### 3.5 Services

#### 3.5.1 Hotkey Service (`services/hotkey.py`)

```python
class HotkeyService:
    def __init__(self):
        self._listener: pynput.keyboard.GlobalHotKeys | None = None
        self._callbacks: dict[str, Callable] = {}
        
    def register(self, hotkey: str, callback: Callable) -> bool:
        """Register a global hotkey. Returns True on success."""
        
    def unregister(self, hotkey: str) -> None:
        """Unregister a previously registered hotkey."""
        
    def unregister_all(self) -> None:
        """Unregister all hotkeys (for shutdown)."""
        
    def start(self) -> None:
        """Start listening for hotkeys."""
        
    def stop(self) -> None:
        """Stop listening for hotkeys."""
        
    @staticmethod
    def parse_hotkey(hotkey_str: str) -> tuple[set[Key], KeyCode]:
        """Parse 'Ctrl+Shift+Space' into pynput format."""
```

**Implementation Notes:**
- Use `pynput.keyboard.GlobalHotKeys` for cross-platform hotkey detection
- Handle platform differences in modifier key names
- Provide feedback if hotkey registration fails (already in use)

#### 3.5.2 Text Inserter (`services/inserter.py`)

```python
class TextInserter:
    def __init__(self, config: ClipboardConfig):
        self.config = config
        self._keyboard = pynput.keyboard.Controller()
        
    def insert(self, text: str) -> bool:
        """
        Insert text at current cursor position.
        
        1. Save current clipboard (if configured)
        2. Copy text to clipboard
        3. Simulate Ctrl+V / Cmd+V
        4. Restore previous clipboard (if configured)
        
        Returns True on success.
        """
        
    def _get_clipboard(self) -> str | None:
        """Get current clipboard text content."""
        
    def _set_clipboard(self, text: str) -> None:
        """Set clipboard text content."""
        
    def _paste(self) -> None:
        """Simulate paste keystroke."""
        
    def _get_paste_keys(self) -> tuple:
        """Return platform-appropriate paste keys."""
```

**Implementation Notes:**
- Use Qt's `QClipboard` for clipboard access (more reliable than pyperclip)
- Small delay between clipboard set and paste simulation
- Catch and log exceptions, don't crash on paste failure

#### 3.5.3 File Watcher (`services/watcher.py`)

```python
class LibraryWatcher:
    def __init__(self, paths: list[Path], on_change: Callable):
        self.paths = paths
        self.on_change = on_change
        self._observer: QFileSystemWatcher | None = None
        
    def start(self) -> None:
        """Start watching library directories for changes."""
        
    def stop(self) -> None:
        """Stop watching."""
        
    def _handle_change(self, path: str) -> None:
        """Debounce and trigger reload callback."""
```

**Implementation Notes:**
- Use Qt's `QFileSystemWatcher` for integration with event loop
- Debounce rapid changes (e.g., editor save operations)
- Only watch directories, not individual files

### 3.6 User Interface

#### 3.6.1 System Tray (`ui/tray.py`)

```python
class SystemTray(QSystemTrayIcon):
    snippet_selected = Signal(Snippet)
    show_palette_requested = Signal()
    settings_requested = Signal()
    reload_requested = Signal()
    quit_requested = Signal()
    
    def __init__(self, library_manager: LibraryManager, parent=None):
        super().__init__(parent)
        self.library_manager = library_manager
        self._build_menu()
        
    def _build_menu(self) -> None:
        """Build context menu from current libraries."""
        
    def rebuild_menu(self) -> None:
        """Rebuild menu after library reload."""
        
    def _create_snippet_submenu(self, library: SnippetLibrary) -> QMenu:
        """Create submenu for a library with category grouping."""
```

#### 3.6.2 Floating Palette (`ui/palette.py`)

```python
class FloatingPalette(QWidget):
    snippet_selected = Signal(Snippet)
    closed = Signal()
    
    def __init__(self, library_manager: LibraryManager, config: PaletteConfig):
        super().__init__()
        self.library_manager = library_manager
        self.config = config
        self._setup_ui()
        self._setup_window_flags()
        
    def _setup_ui(self) -> None:
        """Create layout: filter box, tree view, preview pane."""
        
    def _setup_window_flags(self) -> None:
        """Configure frameless, always-on-top, etc."""
        
    def show_at_position(self) -> None:
        """Show window at configured position."""
        
    def refresh(self) -> None:
        """Rebuild tree from current libraries."""
        
    def _filter_changed(self, text: str) -> None:
        """Update tree view based on filter text."""
        
    def _item_activated(self, item: QTreeWidgetItem) -> None:
        """Handle snippet selection (double-click or Enter)."""
        
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle Escape to close, arrow keys for navigation."""
        
    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Optionally hide on focus loss."""
```

#### 3.6.3 Settings Dialog (`ui/settings.py`)

```python
class SettingsDialog(QDialog):
    config_changed = Signal(Config)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Create tabbed interface with settings controls."""
        
    def _create_general_tab(self) -> QWidget:
        """Hotkey config, palette behavior, clipboard settings."""
        
    def _create_appearance_tab(self) -> QWidget:
        """Theme, font settings."""
        
    def _create_paths_tab(self) -> QWidget:
        """Library path configuration."""
        
    def accept(self) -> None:
        """Validate and emit config_changed before closing."""
```

---

## 4. Implementation Order

### Phase 1: Foundation
1. Project setup (pyproject.toml, directory structure)
2. Configuration module with defaults
3. Snippet and Library data models
4. Library loading from JSON files
5. Unit tests for models and config

### Phase 2: Core Services
1. Text inserter service (clipboard + paste)
2. Hotkey service (global hotkey registration)
3. Basic application class to tie them together
4. Manual testing of insertion mechanism

### Phase 3: Basic UI
1. System tray icon with static menu
2. Dynamic menu building from libraries
3. Snippet selection → insertion flow
4. Application lifecycle (startup, shutdown)

### Phase 4: Floating Palette
1. Basic palette window with tree view
2. Filter/search functionality
3. Preview pane
4. Keyboard navigation
5. Position management

### Phase 5: Settings & Polish
1. Settings dialog
2. Theme support
3. File system watcher for live reload
4. Error handling and logging
5. Edge case testing

### Phase 6: Packaging
1. PyInstaller configuration
2. Platform-specific build scripts
3. Icon resources for each platform
4. Installer/package creation
5. Default snippet libraries

---

## 5. Platform-Specific Considerations

### 5.1 Windows

**Hotkeys:**
- Use `pynput` with default settings
- May need to handle UAC elevation for some applications

**Clipboard:**
- `QClipboard` works reliably
- Some applications may need slight delay before paste

**System Tray:**
- Fully supported by Qt
- Icon should be `.ico` format, 16x16 and 32x32 sizes

**Autostart:**
- Add shortcut to `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`
- Or use registry key `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`

### 5.2 Linux

**Hotkeys:**
- X11: `pynput` works well
- Wayland: May require `python-xlib` fallback or DBus approach
- Consider offering configurable backend

**Clipboard:**
- X11: `QClipboard` works
- Wayland: May need `wl-clipboard` as fallback

**System Tray:**
- Depends on desktop environment
- GNOME: Requires extension (AppIndicator)
- KDE, XFCE: Native support
- Consider fallback to window-only mode

**Autostart:**
- Create `.desktop` file in `~/.config/autostart/`

### 5.3 macOS

**Hotkeys:**
- Requires Accessibility permissions
- Guide user through System Preferences → Security & Privacy → Privacy → Accessibility

**Clipboard:**
- `QClipboard` works reliably
- Use Cmd instead of Ctrl for paste

**System Tray:**
- Menu bar app pattern (fully supported)
- Icon should be template image (monochrome) for menu bar

**Autostart:**
- Add to Login Items in System Preferences
- Or create LaunchAgent plist

**Code Signing:**
- Required for distribution outside App Store
- Consider notarization for Gatekeeper

---

## 6. Testing Strategy

### 6.1 Unit Tests

- Configuration loading/saving
- Library JSON parsing
- Snippet model methods (filtering, matching)
- Hotkey string parsing

### 6.2 Integration Tests

- Library manager loading multiple files
- Full insertion flow (mock clipboard)
- Settings persistence

### 6.3 Manual Testing Checklist

- [ ] Tray icon appears on all platforms
- [ ] Left-click toggles palette
- [ ] Right-click shows menu
- [ ] Menu reflects loaded libraries
- [ ] Snippet selection inserts text
- [ ] Global hotkey summons palette
- [ ] Filter narrows snippet list
- [ ] Escape closes palette
- [ ] Settings changes persist
- [ ] Application survives library file errors
- [ ] Clean shutdown (no orphan processes)

---

## 7. Error Handling

### 7.1 Library Loading Errors

- Log error with file path and reason
- Skip invalid files, continue loading others
- Show notification to user if all libraries fail
- Provide "Reload" action to retry

### 7.2 Hotkey Registration Failures

- Log the conflict
- Show notification that hotkey is in use
- Continue running without hotkey (tray still works)
- Settings dialog should indicate failure

### 7.3 Insertion Failures

- Catch clipboard access errors
- Log failure details
- Don't crash—silently fail or show brief notification
- Consider retry logic for transient failures

---

## 8. Logging

Use Python's `logging` module with:

- File handler: `{app_data}/logs/hug.log`
- Rotating file handler (5MB max, 3 backups)
- Console handler for development
- Log levels: DEBUG for development, INFO for production

Log format:
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Key events to log:
- Application start/stop
- Library loading (count of snippets loaded)
- Hotkey registration success/failure
- Insertion attempts (DEBUG level)
- Configuration changes
- Errors and exceptions

---

## 9. Distribution

### 9.1 PyInstaller Configuration

```python
# build.spec (simplified)
a = Analysis(
    ['src/hug/__main__.py'],
    datas=[
        ('snippets', 'snippets'),
        ('src/hug/resources', 'resources'),
    ],
    hiddenimports=['pynput.keyboard._xorg', 'pynput.mouse._xorg'],
)
```

### 9.2 Build Commands

```bash
# Windows
pyinstaller --onefile --windowed --icon=resources/icons/hug.ico build.spec

# Linux  
pyinstaller --onefile --windowed build.spec

# macOS
pyinstaller --onefile --windowed --icon=resources/icons/hug.icns build.spec
```

### 9.3 Release Artifacts

- Windows: Single `.exe` or MSI installer
- Linux: AppImage or tarball
- macOS: `.app` bundle in DMG

---

## Appendix A: Minimum pyproject.toml

```toml
[project]
name = "hug"
version = "1.0.0"
description = "HuG - Text/Code Snippet Manager"
requires-python = ">=3.10"
dependencies = [
    "PySide6>=6.5.0",
    "pynput>=1.7.6",
]

[project.scripts]
hug = "hug.__main__:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-qt>=4.2.0",
    "black>=23.0.0",
    "mypy>=1.0.0",
    "pyinstaller>=5.0.0",
]

[tool.black]
line-length = 100
target-version = ["py310"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
```
