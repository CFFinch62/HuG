"""File system watcher for libraries."""
import logging
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QObject, QTimer, QFileSystemWatcher, Signal

logger = logging.getLogger(__name__)


class LibraryWatcher(QObject):
    changed = Signal()
    
    def __init__(self, paths: list[str]):
        super().__init__()
        self.paths = [p for p in paths if Path(p).exists()]
        self._watcher = QFileSystemWatcher(self.paths)
        self._watcher.directoryChanged.connect(self._on_change)
        self._watcher.fileChanged.connect(self._on_change)
        
        # Debounce timer
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(500) # 500ms debounce
        self._timer.timeout.connect(self._emit_change)
        
    def _on_change(self, path: str) -> None:
        """Handle file/dir change."""
        logger.debug(f"File system change detected at: {path}")
        self._timer.start()
        
    def _emit_change(self) -> None:
        """Emit signal after debounce."""
        logger.info("Library change confirmed, triggering reload.")
        self.changed.emit()
        
    def update_paths(self, new_paths: list[str]) -> None:
        """Update watched paths."""
        if self._watcher:
            current_paths = self._watcher.directories() + self._watcher.files()
            if current_paths:
                self._watcher.removePaths(current_paths)
                
        valid_paths = [p for p in new_paths if Path(p).exists()]
        if valid_paths:
            self._watcher.addPaths(valid_paths)
            self.paths = valid_paths
