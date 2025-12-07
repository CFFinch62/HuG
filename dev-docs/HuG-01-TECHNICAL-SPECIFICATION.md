# Technical Specification: HuG - Cross-Platform Snippet Manager

**Version:** 1.0  
**Status:** Draft  
**Author:** Chuck / Fragillidae Software  
**Date:** December 2024

---

## 1. Executive Summary

This document specifies HuG (Here U Go), a cross-platform text snippet insertion tool designed for both general writing and programming assistance. The application serves as a teaching aid for beginning programmers, providing structured code templates that require conscious selection rather than passive autocomplete acceptance.

### 1.1 Design Philosophy

HuG bridges the gap between manual typing and full IDE autocomplete. Users must understand what code structure they need and consciously select it, reinforcing learning while reducing repetitive typing. This aligns with a pedagogical approach that emphasizes comprehension over convenience.

### 1.2 Target Users

- Beginning programmers learning code structures
- Writers who frequently use text templates
- Developers who prefer minimal, distraction-free editors
- Instructors teaching programming fundamentals

---

## 2. Functional Requirements

### 2.1 Core Features

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| F01 | System Tray Icon | Required | Persistent tray icon with context menu access to snippets |
| F02 | Floating Palette | Required | Optional always-on-top window for snippet browsing and selection |
| F03 | Global Hotkey | Required | Configurable keyboard shortcut to summon floating palette |
| F04 | Text Insertion | Required | Insert selected snippet at current cursor position in any application |
| F05 | Snippet Categories | Required | Hierarchical organization by type (general, code) and subcategory |
| F06 | Language Libraries | Required | Pre-built snippet collections for common programming languages |
| F07 | JSON Configuration | Required | All snippets defined in human-readable JSON files |
| F08 | Search/Filter | Required | Quick-filter snippets by name or content in floating palette |
| F09 | Palette Toggle | Required | User preference to show/hide floating palette mode |
| F10 | Cross-Platform | Required | Consistent behavior on Windows, Linux, and macOS |

### 2.2 Explicitly Excluded Features

The following features are intentionally NOT included to maintain simplicity:

- **Abbreviation expansion** - No automatic expansion of typed abbreviations
- **Template placeholders** - No tab-stop or variable substitution system
- **Snippet editing GUI** - Users edit JSON files directly
- **Cloud sync** - Local file storage only
- **Plugin system** - Standalone application only (external tools may read JSON files)

### 2.3 Text Insertion Method

The application uses clipboard-based insertion for maximum cross-platform reliability:

1. Store current clipboard contents (optional, configurable)
2. Copy snippet text to clipboard
3. Simulate paste keystroke (Ctrl+V / Cmd+V)
4. Restore previous clipboard contents after brief delay (if enabled)

This approach avoids the complexity and inconsistency of simulating individual keystrokes across different platforms, window managers, and input methods.

---

## 3. User Interface Specifications

### 3.1 System Tray Icon

**Behavior:**
- Single left-click: Toggle floating palette visibility
- Right-click: Show context menu

**Context Menu Structure:**
```
├── [Snippet Categories...]
│   ├── General
│   │   ├── Business Letters
│   │   ├── Email Templates
│   │   └── ...
│   └── Code
│       ├── Python
│       ├── Ruby
│       ├── JavaScript
│       └── ...
├── ─────────────────
├── Show Palette (checkbox)
├── Settings...
├── Reload Snippets
├── ─────────────────
└── Quit
```

### 3.2 Floating Palette Window

**Dimensions:** 300-400px wide, 400-500px tall (user-resizable, remembers size)

**Layout:**
```
┌─────────────────────────────────┐
│ [🔍 Filter...              ] X │  ← Search box + close button
├─────────────────────────────────┤
│ ▼ General                       │  ← Collapsible category
│   ├── Business Letters          │
│   └── Email Templates           │
│ ▼ Python                        │
│   ├── Loops                     │  ← Subcategory
│   │   ├── For Loop              │  ← Snippet (clickable)
│   │   ├── While Loop            │
│   │   └── List Comprehension    │
│   ├── Functions                 │
│   │   ├── Function Definition   │
│   │   └── Lambda Expression     │
│   └── Classes                   │
│ ▶ Ruby (collapsed)              │
│ ▶ JavaScript (collapsed)        │
├─────────────────────────────────┤
│ [Preview of selected snippet]   │  ← Optional preview pane
│ for item in collection:         │
│     # process item              │
│     pass                        │
└─────────────────────────────────┘
```

**Behavior:**
- Frameless or minimal frame, always-on-top
- Appears at last position or near mouse cursor (configurable)
- Hides on: snippet selection, Escape key, focus loss (configurable)
- Filter box has focus when palette appears
- Arrow keys navigate tree, Enter inserts selected snippet
- Double-click on snippet inserts it

### 3.3 Settings Dialog

**General Tab:**
- Global hotkey configuration
- Palette behavior (hide on focus loss, hide on selection)
- Clipboard handling (restore previous contents)
- Start minimized to tray
- Start on system login

**Appearance Tab:**
- Palette position preference (remember last, near cursor, fixed)
- Font family and size for snippet preview
- Theme selection (system, light, dark)

**Paths Tab:**
- Snippet library directories (multiple paths supported)
- Configuration file location (display only)

---

## 4. Data Model

### 4.1 Snippet Library JSON Schema

**File:** `snippets/<category>/<name>.json`

```json
{
  "$schema": "https://fragillidae.software/schemas/snippet-library-v1.json",
  "name": "Python Snippets",
  "description": "Common Python code structures for beginners",
  "language": "python",
  "file_extensions": [".py", ".pyw"],
  "version": "1.0",
  "author": "Fragillidae Software",
  "snippets": [
    {
      "id": "for_loop_basic",
      "name": "For Loop",
      "description": "Iterate over a sequence",
      "category": "loops",
      "tags": ["iteration", "loop", "sequence"],
      "content": "for item in collection:\n    # process item\n    pass"
    }
  ]
}
```

### 4.2 Schema Field Definitions

**Library-Level Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Display name for the library |
| description | string | No | Brief description of library contents |
| language | string | Conditional | Programming language identifier (required for code libraries) |
| file_extensions | array[string] | No | Associated file extensions for this language |
| version | string | No | Semantic version of the library |
| author | string | No | Library author or maintainer |
| snippets | array[Snippet] | Yes | Array of snippet objects |

**Snippet-Level Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes | Unique identifier within library (lowercase, underscores) |
| name | string | Yes | Human-readable display name |
| description | string | No | Brief explanation of the snippet's purpose |
| category | string | No | Subcategory for grouping (e.g., "loops", "functions") |
| tags | array[string] | No | Searchable keywords |
| content | string | Yes | The actual snippet text (use \n for newlines, \t for tabs) |

### 4.3 General Text Snippets

For non-code snippets, omit the `language` field or set it to `"text"`:

```json
{
  "name": "Business Letter Templates",
  "description": "Professional correspondence templates",
  "language": "text",
  "version": "1.0",
  "snippets": [
    {
      "id": "letter_formal",
      "name": "Formal Business Letter",
      "description": "Standard formal letter structure",
      "category": "letters",
      "content": "[Your Name]\n[Your Address]\n..."
    }
  ]
}
```

### 4.4 Application Configuration

**File:** `config.json` (in application data directory)

```json
{
  "version": "1.0",
  "hotkey": {
    "summon_palette": "Ctrl+Shift+Space",
    "insert_last": "Ctrl+Shift+V"
  },
  "palette": {
    "enabled": true,
    "position": "remember",
    "width": 350,
    "height": 450,
    "hide_on_focus_loss": true,
    "hide_on_selection": true,
    "show_preview": true
  },
  "clipboard": {
    "restore_previous": true,
    "restore_delay_ms": 100
  },
  "appearance": {
    "theme": "system",
    "font_family": "monospace",
    "font_size": 12
  },
  "startup": {
    "start_minimized": true,
    "start_on_login": false
  },
  "library_paths": [
    "${APP_DATA}/snippets",
    "${USER_HOME}/.snippets"
  ]
}
```

### 4.5 File System Structure

```
Application Data Directory
├── config.json
├── snippets/
│   ├── general/
│   │   ├── business.json
│   │   ├── email.json
│   │   └── common.json
│   └── code/
│       ├── python.json
│       ├── ruby.json
│       ├── javascript.json
│       ├── racket.json
│       ├── html.json
│       └── css.json
└── logs/
    └── app.log
```

**Platform-Specific Paths:**

| Platform | Application Data Directory |
|----------|---------------------------|
| Windows | `%APPDATA%\HuG\` |
| Linux | `~/.config/hug/` or `$XDG_CONFIG_HOME/hug/` |
| macOS | `~/Library/Application Support/HuG/` |

---

## 5. External Integration

### 5.1 Just Code Integration Path

The snippet JSON files serve as a universal data format. External applications like Just Code can integrate by:

1. Reading JSON files from known snippet directories
2. Parsing the schema documented in Section 4
3. Implementing their own insertion mechanism

No IPC, socket communication, or direct integration is required. This "shared data, no coupling" approach ensures:
- Either tool works independently
- No runtime dependencies between applications
- Simple, file-based data exchange

### 5.2 Just Code Plugin Concept

A Just Code plugin could:
- Watch snippet directories for changes
- Build internal menu/command palette from JSON data
- Insert snippets using Just Code's native text insertion
- Optionally filter snippets by current file's language

This keeps HuG as the "source of truth" for snippet definitions while allowing Just Code to provide integrated access within its editing environment.

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Metric | Requirement |
|--------|-------------|
| Startup time | < 2 seconds to tray icon visible |
| Palette appearance | < 200ms from hotkey press |
| Snippet insertion | < 100ms from selection to paste |
| Memory footprint | < 100MB RAM at idle |
| Library loading | < 500ms for 1000 snippets |

### 6.2 Compatibility

**Operating Systems:**
- Windows 10/11 (64-bit)
- Linux: Ubuntu 20.04+, Fedora 35+, Debian 11+ (X11 and Wayland)
- macOS 11+ (Big Sur and later, including Apple Silicon)

**Python Version:** 3.10 or later

### 6.3 Accessibility

- Keyboard-only navigation of all features
- Screen reader compatible labels on UI elements
- Sufficient color contrast in all themes
- Resizable text in palette and preview

---

## 7. Security Considerations

### 7.1 Snippet Content

Snippets are plain text inserted via clipboard. The application does not:
- Execute snippet content
- Interpret or expand variables/commands within snippets
- Connect to external networks
- Require elevated privileges

### 7.2 File Access

The application reads from:
- Its own configuration directory
- User-specified snippet library paths

The application writes to:
- Its own configuration file
- Log files in application data directory

No other file system access is required or permitted.

---

## 8. Future Considerations

The following features are explicitly out of scope for version 1.0 but may be considered for future versions:

- Optional template placeholders with tab navigation
- Snippet editor GUI
- Import/export of snippet libraries
- Snippet usage statistics
- Context-aware filtering (detect active application's file type)

These should not influence the v1.0 architecture but the design should not preclude their future addition.

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| Snippet | A reusable text fragment stored for quick insertion |
| Library | A JSON file containing related snippets |
| Category | A grouping of snippets within a library |
| Palette | The floating window displaying available snippets |
| Tray Icon | The system notification area icon |

---

## Appendix B: Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | Chuck | Initial specification |
