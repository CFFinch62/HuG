# Changelog - Session 1 Fixes

## Date: 2025-12-07

### Summary
Fixed critical issues with snippet insertion and global hotkey detection on Linux. Created comprehensive snippet libraries for 10 programming languages.

---

## Snippet Libraries Created

Created **10 snippet libraries** with **236 total snippets** in `snippets/code/`:

| Library | File | Snippets |
|---------|------|----------|
| Python Basics | `python-basics.json` | 45 |
| JavaScript Basics | `javascript-basics.json` | 38 |
| TypeScript Basics | `typescript-basics.json` | 17 |
| Java Basics | `java-basics.json` | 20 |
| C# Basics | `csharp-basics.json` | 20 |
| Go Basics | `go-basics.json` | 20 |
| Rust Basics | `rust-basics.json` | 20 |
| Bash Basics | `bash-basics.json` | 18 |
| SQL Basics | `sql-basics.json` | 18 |
| HTML & CSS Basics | `html-css-basics.json` | 20 |

---

## Bug Fixes

### 1. Libraries Not Loading from Config
**Problem:** When config file existed with empty `library_paths: []`, no libraries loaded.

**Solution:** Modified `Config.load()` in `src/hug/config.py` to use default paths when `library_paths` is empty.

### 2. Incorrect Path Resolution
**Problem:** `get_default_library_paths()` went up 4 parent directories instead of 3, landing in wrong folder.

**Solution:** Fixed parent traversal from `.parent.parent.parent.parent` to `.parent.parent.parent`.

### 3. Settings Menu Disappearing After Use
**Problem:** After opening Settings dialog, the tray menu only showed "Quit" on subsequent right-clicks.

**Solution:** 
- Added `settings_requested` Signal to `SystemTray` class
- Connected Settings action inside `_build_menu()` to emit this signal
- Signal connection survives menu rebuilds

### 4. Snippet Paste Not Working (pynput issue)
**Problem:** pynput's keyboard simulation doesn't work on Linux due to X11/Wayland permission issues. Ctrl+V keystrokes weren't being received by VSCode.

**Solution:**
- Added `xdotool` support for Linux (requires: `sudo apt install xdotool`)
- Modified `TextInserter._paste()` to use xdotool when available
- Added window focus tracking to restore focus before pasting

### 5. Clipboard Restore Interfering with Paste
**Problem:** The "restore previous clipboard" feature was restoring old content before the paste completed, causing wrong content to be pasted.

**Solution:** Disabled clipboard restore feature. Snippet now stays on clipboard after insertion.

### 6. Global Hotkey Not Working (pynput issue)
**Problem:** pynput's `GlobalHotKeys` listener doesn't detect keypresses on Linux.

**Solution:**
- Rewrote `HotkeyService` in `src/hug/services/hotkey.py`
- Added Xlib-based hotkey listener for Linux using X11 key grabbing
- Falls back to pynput on other platforms (macOS, Windows)

---

## Files Modified

- `src/hug/config.py` - Fixed path resolution and empty library_paths handling
- `src/hug/app.py` - Added tray menu signal connections, window save on menu show
- `src/hug/ui/tray.py` - Added `settings_requested` and `menu_about_to_show` signals
- `src/hug/services/inserter.py` - Added xdotool support, window focus restoration
- `src/hug/services/hotkey.py` - Complete rewrite with Xlib backend for Linux

## Files Created

- `snippets/code/python-basics.json`
- `snippets/code/javascript-basics.json`
- `snippets/code/typescript-basics.json`
- `snippets/code/java-basics.json`
- `snippets/code/csharp-basics.json`
- `snippets/code/go-basics.json`
- `snippets/code/rust-basics.json`
- `snippets/code/bash-basics.json`
- `snippets/code/sql-basics.json`
- `snippets/code/html-css-basics.json`

---

## Dependencies

**New system dependency required on Linux:**
```bash
sudo apt install xdotool
```

**Python dependencies (already installed):**
- `python-xlib` - Used by new Xlib hotkey listener

---

## Testing Status

- ✅ Tray menu displays all 10 libraries
- ✅ Snippet selection auto-pastes into editor
- ✅ Global hotkey (Ctrl+Shift+Space) opens floating palette
- ✅ Settings menu persists after use

