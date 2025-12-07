"""Tests for Library Watcher."""
import os
import time
from unittest.mock import MagicMock
from pathlib import Path

from PySide6.QtCore import QTimer

from hug.services.watcher import LibraryWatcher


def test_watcher_debounce(qtbot, tmp_path):
    # Create temp dir to watch
    watch_dir = tmp_path / "snippets"
    watch_dir.mkdir()
    
    # Init watcher
    watcher = LibraryWatcher([str(watch_dir)])
    
    # Mock signal
    with qtbot.waitSignal(watcher.changed, timeout=1000) as blocker:
        # Create a file
        (watch_dir / "test.json").touch()
        
    assert blocker.signal_triggered
    
def test_watcher_update_paths(qtbot, tmp_path):
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    dir2 = tmp_path / "dir2"
    dir2.mkdir()
    
    watcher = LibraryWatcher([str(dir1)])
    
    # Update to watch dir2
    watcher.update_paths([str(dir2)])
    
    # Change in dir1 shouldn't trigger
    with qtbot.assertNotEmitted(watcher.changed):
        (dir1 / "file.txt").touch()
        # Wait for potential timer
        qtbot.wait(600)
        
    # Change in dir2 SHOULD trigger
    with qtbot.waitSignal(watcher.changed, timeout=1000):
        (dir2 / "file.txt").touch()
