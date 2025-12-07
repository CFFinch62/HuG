"""Text insertion service."""
import logging
import shutil
import subprocess
import sys
import time
from typing import cast

from PySide6.QtGui import QClipboard, QGuiApplication
from pynput.keyboard import Controller, Key, KeyCode

from hug.config import ClipboardConfig

logger = logging.getLogger(__name__)

# Check for xdotool on Linux
XDOTOOL_PATH = shutil.which("xdotool") if sys.platform == "linux" else None


class TextInserter:
    def __init__(self, config: ClipboardConfig):
        self.config = config
        self._keyboard = Controller()
        self._last_active_window: str | None = None

    def save_active_window(self) -> None:
        """Save the currently active window ID (call before showing menu)."""
        if sys.platform == "linux" and XDOTOOL_PATH:
            try:
                result = subprocess.run(
                    [XDOTOOL_PATH, "getactivewindow"],
                    capture_output=True, text=True, timeout=2
                )
                self._last_active_window = result.stdout.strip()
                logger.info(f"Saved active window ID: {self._last_active_window}")
            except Exception as e:
                logger.warning(f"Could not save active window: {e}")
                self._last_active_window = None

    def insert(self, text: str) -> bool:
        """
        Insert text at current cursor position.

        1. Save current clipboard (if configured)
        2. Copy text to clipboard
        3. Wait for focus to return to previous window
        4. Simulate Ctrl+V / Cmd+V
        5. Restore previous clipboard (if configured)

        Returns True on success.
        """
        try:
            clipboard = QGuiApplication.clipboard()
            if not clipboard:
                logger.error("Could not access QClipboard")
                return False

            previous_text = None
            if self.config.restore_previous:
                previous_text = clipboard.text()

            # Set new text
            logger.info(f"Setting clipboard text (first 50 chars): {text[:50] if len(text) > 50 else text}")
            clipboard.setText(text)

            # Verify clipboard was set
            verify = clipboard.text()
            logger.info(f"Clipboard verification (first 50 chars): {verify[:50] if len(verify) > 50 else verify}")

            # Wait for menu to close and focus to return to previous window
            # This delay is critical for tray menu selections
            time.sleep(0.2)

            # Simulate paste
            self._paste()

            # NOTE: Clipboard restore is disabled - it interferes with paste timing
            # The snippet stays on clipboard which is actually more useful
            # if self.config.restore_previous and previous_text is not None:
            #     restore_delay = max(self.config.restore_delay_ms, 500) / 1000.0
            #     time.sleep(restore_delay)
            #     clipboard.setText(previous_text)
            #     logger.info("Clipboard restored to previous content")

            return True
            
        except Exception as e:
            logger.error(f"Insertion failed: {e}")
            return False

    def _paste(self) -> None:
        """Simulate paste keystroke."""
        try:
            logger.info(f"Simulating paste on platform: {sys.platform}")

            # On Linux, prefer xdotool if available (more reliable)
            if sys.platform == "linux" and XDOTOOL_PATH:
                logger.info("Using xdotool for paste simulation")

                # Restore focus to the saved window first
                if self._last_active_window:
                    logger.info(f"Restoring focus to window: {self._last_active_window}")
                    try:
                        subprocess.run(
                            [XDOTOOL_PATH, "windowactivate", "--sync", self._last_active_window],
                            check=True, timeout=2
                        )
                        time.sleep(0.05)  # Small delay after focus restore
                    except Exception as e:
                        logger.warning(f"Could not restore focus: {e}")

                # Send Ctrl+V to the focused window
                subprocess.run(
                    [XDOTOOL_PATH, "key", "--clearmodifiers", "ctrl+v"],
                    check=True, timeout=2
                )
            elif sys.platform == 'darwin':
                with self._keyboard.pressed(Key.cmd):
                    self._keyboard.press('v')
                    self._keyboard.release('v')
            else:
                # Fallback to pynput
                with self._keyboard.pressed(Key.ctrl):
                    self._keyboard.press('v')
                    self._keyboard.release('v')
            logger.info("Paste simulation completed")
        except subprocess.TimeoutExpired:
            logger.error("xdotool timed out")
        except subprocess.CalledProcessError as e:
            logger.error(f"xdotool failed: {e}")
        except Exception as e:
            logger.error(f"Failed to simulate paste keys: {e}")
