# Phase 2: Core Services - Changelog

**Goal:** Implement the core backend services, data models, and application structure for HuG.

## Changes

### 2025-12-06
- **Configuration Module (`src/hug/config.py`):**
    - Implemented `Config` class with JSON loading/saving.
    - Defined default configuration for Hotkeys, Palette, Clipboard, etc.
- **Data Models (`src/hug/models/`):**
    - Implemented `Snippet` dataclass.
    - Implemented `SnippetLibrary` matching new JSON schema.
    - Implemented `LibraryManager` for loading multiple libraries.
- **Services (`src/hug/services/`):**
    - Implemented `TextInserter` using `PySide6.QtGui.QClipboard` and `pynput`.
    - Implemented `HotkeyService` using `pynput.keyboard.GlobalHotKeys`.
- **Application Core:**
    - Created `HugApp` class in `src/hug/app.py`.
    - Created entry point in `src/hug/__main__.py`.
- **Testing:**
    - Added unit tests for Configuration and Models.
    - Verified text insertion and hotkey registration logic.
