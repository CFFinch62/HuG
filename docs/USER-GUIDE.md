# HuG User Guide

## Introduction

**HuG** is a lightweight, cross-platform snippet manager designed to keep your most-used text and code blocks at your fingertips. Whether you're a developer needing quick access to boilerplate code or a writer managing canned responses, HuG helps you stay in the flow.

## Installation

### From Release (Recommended)
1. Download the latest release archive (e.g., `hug-linux.zip`, `hug-windows.zip`) from the releases page.
2. Extract the archive to a folder of your choice.
3. Locate the `hug` executable (or `hug.exe` on Windows) inside the extracted folder.
4. (Optional) Create a shortcut to this executable on your Desktop or Taskbar for easy access.

### From Source
If you prefer to run from source code:
1. Ensure you have Python 3.10+ installed.
2. Clone the repository.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the application: `python -m hug`.

## Getting Started

### Launching HuG
Double-click the `hug` executable to start the application.
- You will see the **HuG icon** appear in your **System Tray** (near the clock).
- The application runs in the background, waiting for your command.

### The System Tray
The System Tray icon is your primary indicator that HuG is running.
- **Right-Click** the icon to open the menu.
- **Browse Snippets**: Navigate through your loaded libraries and categories directly from the menu. Clicking a snippet will insert it into your active window.
- **Settings**: Open the configuration dialog.
- **Quit**: Exit the application.

## Core Features

### 1. The Floating Palette
The heart of HuG is the Floating Palette, a keyboard-centric search window.

- **Summon**: Press the global hotkey (**Default**: `Ctrl+Shift+Space`) to open the palette anywhere.
- **Search**: Immediately start typing to filter your snippets. The results update in real-time.
- **Navigate**: Use the **Up** and **Down** arrow keys to browse the results list.
- **Preview**: As you select a snippet, the **Preview Pane** on the right shows the full content.
- **Insert**: Press **Enter** to paste the selected snippet into your previously active application.
- **Dismiss**: Press **Escape** or click anywhere outside the palette to close it without inserting.

### 2. Snippet Management
HuG uses simple JSON files to store your snippets, making them easy to edit, back up, and share.

#### Snippet Libraries
Snippets are organized into **Libraries** (folders) containing `.json` files.
- By default, HuG looks for snippets in the `snippets/` folder next to the executable.
- You can add your own custom folders in the **Settings**.

#### Creating/Editing Snippets
Currently, you manage snippets by editing the JSON files directly.
1. Open any `.json` file in the `snippets/` folder using a text editor (Notepad, VS Code, etc.).
2. Add a new entry following this format:
   ```json
   {
       "id": "unique-id-123",
       "name": "My Snippet Name",
       "content": "The actual text to paste goes here.\nIt can be multi-line.",
       "description": "Optional tooltip description",
       "category": "My Category",
       "tags": ["tag1", "tag2"]
   }
   ```
3. **Save the file**. HuG will automatically detect the change and reload your library instantly!

### 3. Settings & Customization
Right-click the tray icon and select **Settings** to customize HuG.

- **General**:
    - **Summon Hotkey**: Click the input box and press your desired key combination to change the global shortcut.
    - **Restore Clipboard**: If checked, HuG will attempt to restore your previous clipboard content after pasting a snippet (experimental).
- **Appearance**: Adjust the **Width** and **Height** of the Floating Palette to suit your screen.
- **Libraries**: Add paths to other folders where you store snippet JSON files. This allows you to keep your personal snippets separate from the defaults (e.g., in a Dropbox folder).

## Troubleshooting

### "The hotkey doesn't work!"
- Check if another application is using `Ctrl+Shift+Space`.
- Go to Settings and try binding a different combination (e.g., `Ctrl+Alt+H`).
- On Linux, ensure you have the necessary permissions if using Wayland (X11 is recommended for best compatibility).

### "My snippets aren't showing up."
- Ensure your JSON file is valid. You can use an online JSON validator to check for syntax errors.
- Check the **Libraries** tab in Settings to ensure the folder path is correct.

### "It won't paste into my game/terminal."
- Some applications block simulated input. Try running HuG as Administrator (Windows) or `sudo` (Linux) if necessary, though this is generally not recommended for security reasons.
