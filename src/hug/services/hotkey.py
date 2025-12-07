"""Global hotkey service."""
import logging
from typing import Callable

from pynput import keyboard

logger = logging.getLogger(__name__)


class HotkeyService:
    def __init__(self):
        self._listener: keyboard.GlobalHotKeys | None = None
        self._callbacks: dict[str, Callable] = {}
        self._input_hotkeys: dict[str, Callable] = {}
        
    def register(self, hotkey: str, callback: Callable) -> bool:
        """
        Register a global hotkey. 
        Note: Actual registration happens on start().
        """
        try:
            # Validate basic format locally if needed,
            # but rely on pynput parsing primarily.
            self._input_hotkeys[hotkey] = callback
            return True
        except Exception as e:
            logger.error(f"Failed to register hotkey {hotkey}: {e}")
            return False
            
    def unregister_all(self) -> None:
        """Stop listening."""
        self.stop()
        self._input_hotkeys.clear()
        
    def start(self) -> None:
        """Start listening for hotkeys."""
        if self._listener:
            self.stop()
            
        try:
            # Create mapping for pynput
            # pynput expects a dict of {string: callable}
            # We normalize strings to use <modifier> format for reliability
            hotkey_map = {}
            for hk_str, cb in self._input_hotkeys.items():
                # Simple normalization
                norm_hk = hk_str.lower() \
                    .replace('ctrl', '<ctrl>') \
                    .replace('shift', '<shift>') \
                    .replace('alt', '<alt>') \
                    .replace('cmd', '<cmd>') \
                    .replace('super', '<cmd>') \
                    .replace('space', '<space>') \
                    .replace('enter', '<enter>') \
                    .replace('return', '<enter>') \
                    .replace('tab', '<tab>') \
                    .replace('esc', '<esc>')
                    
                hotkey_map[norm_hk] = cb
            
            logger.info(f"Starting hotkey listener with: {list(hotkey_map.keys())}")
            self._listener = keyboard.GlobalHotKeys(hotkey_map)
            self._listener.start()
        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            self._listener = None
        
    def stop(self) -> None:
        """Stop listening for hotkeys."""
        if self._listener:
            self._listener.stop()
            self._listener = None
            logger.info("Hotkey listener stopped")
