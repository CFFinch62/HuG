# Phase 5: Settings & Polish - Changelog

**Goal:** Implement user-configurable settings and live library reloading.

## Changes

### 2025-12-06
- **Settings Dialog (`src/hug/ui/settings.py`):**
    - Implemented `SettingsDialog` with tabbed interface.
    - **General**: Configurable Global Hotkey, Clipboard behavior.
    - **Appearance**: Palette dimensions.
    - **Libraries**: Editable list of library paths.
    - Implemented signal-based configuration updates to `HugApp`.
- **Library Watcher (`src/hug/services/watcher.py`):**
    - Implemented `LibraryWatcher` using `QFileSystemWatcher`.
    - Added debounce logic to prevent double-reloading.
    - Connected watcher to `LibraryManager.reload()`.
- **App Integration (`src/hug/app.py`):**
    - Added "Settings" menu item to System Tray.
    - Implemented dynamic hotkey re-registration on config change.
    - Connected Watcher signals to live-reload UI (Tray and Palette).
- **Testing:**
    - Added `tests/test_services_watcher.py` to verify file monitoring and signal debouncing.
