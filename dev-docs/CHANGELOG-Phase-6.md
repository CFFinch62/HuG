# Phase 6: Packaging - Changelog

**Goal:** Create a standalone executable and release archive.

## Changes

### 2025-12-06
- **Build Configuration (`package/hug.spec`):**
    - Configured PyInstaller spec to include `hug` package, resources, and snippets.
    - Added hidden imports for `pynput` and `Xlib` (Linux support).
    - Configured strict hotkey parsing fix.
- **Build Script (`scripts/build.py`):**
    - Created automation script to clean build dirs and run PyInstaller.
    - Added automatic ZIP archive creation for releases.
- **Hotfixes:**
    - Updated `HotkeyService` to normalize hotkey strings (e.g., `Ctrl` -> `<ctrl>`, `Space` -> `<space>`) to resolve runtime errors in the frozen environment.
- **Artifacts:**
    - Generated `dist/hug` (Executable directory).
    - Generated `dist/hug-linux.zip` (Release archive).
