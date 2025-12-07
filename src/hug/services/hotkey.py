"""Global hotkey service."""
import logging
import sys
import threading
from typing import Callable

logger = logging.getLogger(__name__)


class HotkeyService:
    """
    Global hotkey service with platform-specific backends.

    On Linux: Uses Xlib for reliable hotkey detection
    On other platforms: Falls back to pynput
    """

    def __init__(self):
        self._listener_thread: threading.Thread | None = None
        self._running = False
        self._input_hotkeys: dict[str, Callable] = {}

    def register(self, hotkey: str, callback: Callable) -> bool:
        """
        Register a global hotkey.
        Note: Actual registration happens on start().
        """
        try:
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
        if self._listener_thread and self._listener_thread.is_alive():
            self.stop()

        self._running = True

        if sys.platform == "linux":
            self._listener_thread = threading.Thread(
                target=self._xlib_listener, daemon=True
            )
        else:
            self._listener_thread = threading.Thread(
                target=self._pynput_listener, daemon=True
            )

        self._listener_thread.start()
        logger.info("Hotkey listener started")

    def _xlib_listener(self) -> None:
        """Linux hotkey listener using Xlib."""
        try:
            from Xlib import X, XK
            from Xlib.display import Display

            display = Display()
            root = display.screen().root

            # Parse and grab hotkeys
            for hk_str, callback in self._input_hotkeys.items():
                keycode, modmask = self._parse_hotkey_xlib(display, hk_str)
                if keycode:
                    # Grab with and without NumLock (Mod2Mask)
                    root.grab_key(keycode, modmask, True, X.GrabModeAsync, X.GrabModeAsync)
                    root.grab_key(keycode, modmask | X.Mod2Mask, True, X.GrabModeAsync, X.GrabModeAsync)
                    logger.info(f"Grabbed hotkey: {hk_str} (keycode={keycode}, modmask={modmask})")

            logger.info("Xlib hotkey listener running")

            while self._running:
                # Check for events with timeout
                if display.pending_events():
                    event = display.next_event()
                    if event.type == X.KeyPress:
                        # Find matching callback
                        for hk_str, callback in self._input_hotkeys.items():
                            keycode, modmask = self._parse_hotkey_xlib(display, hk_str)
                            # Check keycode matches, and modifiers match (ignoring NumLock)
                            event_mods = event.state & ~X.Mod2Mask
                            if event.detail == keycode and (event_mods & modmask) == modmask:
                                logger.info(f"Hotkey triggered: {hk_str}")
                                callback()
                                break
                else:
                    # Small sleep to avoid busy loop
                    import time
                    time.sleep(0.05)

            # Ungrab keys on stop
            for hk_str, callback in self._input_hotkeys.items():
                keycode, modmask = self._parse_hotkey_xlib(display, hk_str)
                if keycode:
                    root.ungrab_key(keycode, modmask)
                    root.ungrab_key(keycode, modmask | X.Mod2Mask)

            display.close()
            logger.info("Xlib hotkey listener stopped")

        except Exception as e:
            logger.error(f"Xlib hotkey listener error: {e}")
            # Fall back to pynput
            self._pynput_listener()

    def _parse_hotkey_xlib(self, display, hk_str: str) -> tuple[int | None, int]:
        """Parse hotkey string to Xlib keycode and modifier mask."""
        from Xlib import X, XK

        parts = hk_str.lower().replace('+', ' ').split()
        modmask = 0
        key = None

        for part in parts:
            part = part.strip()
            if part in ('ctrl', 'control'):
                modmask |= X.ControlMask
            elif part == 'shift':
                modmask |= X.ShiftMask
            elif part in ('alt', 'meta'):
                modmask |= X.Mod1Mask
            elif part in ('super', 'win', 'cmd'):
                modmask |= X.Mod4Mask
            else:
                key = part

        if not key:
            return None, modmask

        # Get keysym for key
        if key == 'space':
            keysym = XK.XK_space
        elif key == 'enter' or key == 'return':
            keysym = XK.XK_Return
        elif key == 'tab':
            keysym = XK.XK_Tab
        elif key == 'esc' or key == 'escape':
            keysym = XK.XK_Escape
        elif key == 'backspace':
            keysym = XK.XK_BackSpace
        elif len(key) == 1:
            keysym = XK.string_to_keysym(key)
        else:
            keysym = XK.string_to_keysym(key.capitalize())

        keycode = display.keysym_to_keycode(keysym)
        return keycode, modmask

    def _pynput_listener(self) -> None:
        """Fallback pynput listener for non-Linux platforms."""
        try:
            from pynput import keyboard

            hotkey_map = {}
            for hk_str, cb in self._input_hotkeys.items():
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

            logger.info(f"Starting pynput listener with: {list(hotkey_map.keys())}")
            listener = keyboard.GlobalHotKeys(hotkey_map)
            listener.start()

            while self._running:
                import time
                time.sleep(0.1)

            listener.stop()
            logger.info("pynput hotkey listener stopped")

        except Exception as e:
            logger.error(f"pynput hotkey listener error: {e}")

    def stop(self) -> None:
        """Stop listening for hotkeys."""
        self._running = False
        if self._listener_thread:
            self._listener_thread.join(timeout=1.0)
            self._listener_thread = None
            logger.info("Hotkey listener stopped")
