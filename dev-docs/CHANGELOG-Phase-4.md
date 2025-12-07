# Phase 4: Floating Palette - Changelog

**Goal:** Implement the Floating Palette (search/filtering UI).

## Changes

### 2025-12-06
- **UI Widgets (`src/hug/ui/widgets/`):**
    - Implemented `SnippetTree` for hierarchical display and filtering.
    - Implemented `PreviewPane` for snippet content preview.
- **Palette Window (`src/hug/ui/palette.py`):**
    - Implemented `FloatingPalette` window (Frameless, Always-on-Top).
    - Added Search Bar with real-time filtering updates.
    - Added Splitter layout for Tree and Preview.
    - Implemented Keyboard Navigation (Arrow keys act on tree while focused in search).
    - Implemented Window positioning logic.
- **App Integration (`src/hug/app.py`):**
    - Initialized `FloatingPalette`.
    - Connected Summon Hotkey to show palette.
- **Testing:**
    - Added `tests/test_ui_palette.py` to verify search filtering logic.
