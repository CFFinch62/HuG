"""Core application class."""
import logging
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication

from hug.config import Config
from hug.models.library import LibraryManager
from hug.services.hotkey import HotkeyService
from hug.services.inserter import TextInserter
from hug.services.watcher import LibraryWatcher
from hug.ui.tray import SystemTray
from hug.ui.palette import FloatingPalette
from hug.ui.settings import SettingsDialog
from hug.models.snippet import Snippet

logger = logging.getLogger(__name__)


class HugApp(QObject):
    def __init__(self, argv: list[str]):
        """Initialize application components."""
        super().__init__()
        self._qapp = QApplication(argv)
        self._qapp.setQuitOnLastWindowClosed(False)
        
        # Load config
        config_path = Config.get_default_paths() / "config.json"
        self.config = Config.load(config_path)
        
        # Initialize components
        self.library_manager = LibraryManager(self.config.library_paths)
        self.inserter = TextInserter(self.config.clipboard)
        self.hotkey_service = HotkeyService()
        self.watcher = LibraryWatcher(self.config.library_paths)
        
        # UI Components
        self.tray: SystemTray | None = None
        self.palette: FloatingPalette | None = None
        self.settings_dialog: SettingsDialog | None = None
        
        self._setup_services()
        self._setup_ui()
        
    def _setup_services(self) -> None:
        """Connect services."""
        # Load libraries
        self.library_manager.load_all()
        
        # Watcher
        self.watcher.changed.connect(self.reload_libraries)
        
        # Register global hotkey
        self._register_hotkey()
        self.hotkey_service.start()
        
    def _register_hotkey(self) -> None:
        """Register hotkey from config."""
        # Clear existing first (if re-registering)
        self.hotkey_service.unregister_all()
        
        hotkey = self.config.hotkey.summon_palette
        if hotkey:
            logger.info(f"Registering summon hotkey: {hotkey}")
            self.hotkey_service.register(hotkey, self.on_summon)
            self.hotkey_service.start() # Restart listener if needed
            
    def _setup_ui(self) -> None:
        """Initialize UI components."""
        icon_path = str(Path(__file__).parent / "resources" / "icons" / "hug.png")
        self.tray = SystemTray(self.library_manager, icon_path)
        
        # Initialize Palette
        self.palette = FloatingPalette(self.library_manager, self.config.palette)
        
        # Connect signals
        self.tray.snippet_selected.connect(self.on_snippet_selected)
        self.tray.quit_requested.connect(self.quit)
        
        # Add Settings Action to Tray
        settings_action = self.tray.menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)
        
        self.palette.snippet_selected.connect(self.on_snippet_selected)
        
    @Slot()
    def on_summon(self) -> None:
        """Handle summon hotkey."""
        logger.info("Summon hotkey pressed!")
        if self.palette:
            self.palette.show_at_position()
            
    @Slot(Snippet)
    def on_snippet_selected(self, snippet: Snippet) -> None:
        """Handle snippet selection from tray."""
        logger.info(f" inserting snippet: {snippet.name}")
        success = self.inserter.insert(snippet.content)
        if not success:
            logger.error("Failed to insert snippet")

    @Slot()
    def reload_libraries(self) -> None:
        """Reload libraries from disk."""
        logger.info("Reloading libraries...")
        self.library_manager.reload()
        if self.tray:
            self.tray.rebuild_menu()
        if self.palette:
            self.palette.refresh()
            
    @Slot()
    def show_settings(self) -> None:
        """Show settings dialog."""
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog(self.config)
            self.settings_dialog.config_changed.connect(self.on_config_changed)
            
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
        
    @Slot(Config)
    def on_config_changed(self, new_config: Config) -> None:
        """Handle config updates."""
        logger.info("Configuration changed")
        self.config = new_config
        self.config.save(Config.get_default_paths() / "config.json")
        
        # Apply changes
        self._register_hotkey()
        self.watcher.update_paths(self.config.library_paths)
        self.library_manager.library_paths = [Path(p) for p in self.config.library_paths]
        self.reload_libraries()
        
        # Resize palette
        if self.palette:
            self.palette.resize(self.config.palette.width, self.config.palette.height)

    def run(self) -> int:
        """Start message loop."""
        try:
            return self._qapp.exec()
        finally:
            self.quit()
            
    @Slot()
    def quit(self) -> None:
        """Cleanup and exit."""
        logger.info("Shutting down...")
        self.hotkey_service.stop()
        self.config.save(Config.get_default_paths() / "config.json")
        self._qapp.quit()
