# HuG

**Your snippets, one keystroke away.**

---

## What It Does

HuG (Here U Go) is a lightweight snippet manager that lives in your system tray, ready to insert your most-used text and code blocks into any application with a single hotkey. Press `Ctrl+Shift+Space`, search for what you need, hit Enter—done.

## The Problem It Solves

Developers and writers constantly retype the same boilerplate code, email responses, or text templates. Copy-pasting from files breaks your flow. IDE autocomplete is great, but it doesn't work everywhere, and it can be *too* automatic—especially for learners who benefit from consciously selecting the structure they need.

HuG gives you instant access to your snippets in *any* application—your terminal, email client, browser, or minimal text editor—without the cognitive overhead of remembering where you saved that template.

## Key Features

- **Global Hotkey** — Summon the floating palette from anywhere with `Ctrl+Shift+Space` (customizable)
- **Instant Search** — Start typing to filter hundreds of snippets in milliseconds
- **Live Preview** — See the full snippet before inserting it
- **System Tray Access** — Browse snippets by category directly from the tray menu
- **JSON-Based Libraries** — Human-readable snippet files you can edit, share, and version control
- **Live Reload** — Edit your JSON files and see changes instantly—no restart required
- **Cross-Platform** — Works identically on Windows, Linux, and macOS

## Who It's For

- **Beginning programmers** learning code structures who want to select snippets consciously rather than rely on autocomplete
- **Writers** who frequently use canned responses, templates, or boilerplate text
- **Developers** who work in minimal editors without built-in snippet support
- **Anyone** tired of hunting through files for that one piece of text they use every day

## Platform Support

- Windows 10/11
- Linux (Ubuntu, Fedora, Debian — X11 recommended, Wayland supported)
- macOS 11+ (Big Sur and later, including Apple Silicon)

## Getting Started

1. Download the release for your platform
2. Extract and run the `hug` executable
3. Press `Ctrl+Shift+Space` to open the palette
4. Start typing to find a snippet, then press `Enter` to insert

Your snippets live in simple JSON files in the `snippets/` folder—edit them with any text editor to customize your library.

## Technology

Built with Python and Qt (PySide6) for native look and feel across all platforms. Snippets are stored as plain JSON files—no database, no cloud sync, no lock-in.

---

**Fragillidae Software** — Old School meets New School
