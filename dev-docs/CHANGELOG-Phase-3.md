# Phase 3: Basic UI - Changelog

**Goal:** Implement the System Tray interface and connect it to core services.

## Changes

### 2025-12-06
- **Resources:**
    - Added `src/hug/resources/icons/hug.png` (application icon).
- **User Interface (`src/hug/ui/tray.py`):**
    - Implemented `SystemTray` class.
    - Added dynamic menu building from `LibraryManager`.
    - Implemented category grouping support in menus.
    - Connected menu actions to `snippet_selected` signal.
- **Application Core (`src/hug/app.py`):**
    - Initialized `SystemTray` in `HugApp`.
    - Connected `snippet_selected` signal to `TextInserter`.
    - Implemented proper `quit` logic connected to Tray menu.
- **Testing:**
    - Added `tests/test_ui_tray.py` to verify dynamic menu construction.
