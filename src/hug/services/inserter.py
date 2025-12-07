"""Text insertion service."""
import logging
import time
from typing import cast

from PySide6.QtGui import QClipboard, QGuiApplication
from pynput.keyboard import Controller, Key, KeyCode

from hug.config import ClipboardConfig

logger = logging.getLogger(__name__)


class TextInserter:
    def __init__(self, config: ClipboardConfig):
        self.config = config
        self._keyboard = Controller()
        
    def insert(self, text: str) -> bool:
        """
        Insert text at current cursor position.
        
        1. Save current clipboard (if configured)
        2. Copy text to clipboard
        3. Simulate Ctrl+V / Cmd+V
        4. Restore previous clipboard (if configured)
        
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
            clipboard.setText(text)
            
            # Wait for clipboard system to update
            # This is critical on some platforms
            time.sleep(0.1) 
            
            # Simulate paste
            self._paste()
            
            # Optional restore
            if self.config.restore_previous and previous_text:
                # Wait for paste to complete before restoring
                time.sleep(self.config.restore_delay_ms / 1000.0)
                clipboard.setText(previous_text)
                
            return True
            
        except Exception as e:
            logger.error(f"Insertion failed: {e}")
            return False

    def _paste(self) -> None:
        """Simulate paste keystroke."""
        try:
            # Platform specific paste keys
            import sys
            if sys.platform == 'darwin':
                with self._keyboard.pressed(Key.cmd):
                    self._keyboard.press('v')
                    self._keyboard.release('v')
            else:
                with self._keyboard.pressed(Key.ctrl):
                    self._keyboard.press('v')
                    self._keyboard.release('v')
        except Exception as e:
            logger.error(f"Failed to simulate paste keys: {e}")
