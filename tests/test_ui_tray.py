"""Tests for System Tray logic."""
from unittest.mock import MagicMock
from PySide6.QtWidgets import QMenu

from hug.ui.tray import SystemTray
from hug.models.library import LibraryManager, SnippetLibrary, Snippet


def test_tray_menu_building(qtbot):
    # Mock LibraryManager
    manager = MagicMock(spec=LibraryManager)
    
    # Create sample library
    snippets = [
        Snippet(id="1", name="Snip1", content="c1", category="Cat1"),
        Snippet(id="2", name="Snip2", content="c2", category="Cat1"),
        Snippet(id="3", name="Snip3", content="c3", category=""),
    ]
    lib = SnippetLibrary(name="TestLib", snippets=snippets)
    
    manager.libraries = {"TestLib": lib}
    
    # Create Tray (mock icon path)
    tray = SystemTray(manager, "icon.png")
    qtbot.addWidget(tray.menu) # Manage lifecycle
    
    # Verify Menu Structure
    # Top level should have "TestLib"
    assert len(tray.menu.actions()) >= 2 # TestLib + Separator + Quit
    
    lib_action = next(a for a in tray.menu.actions() if a.text() == "TestLib")
    lib_menu = lib_action.menu()
    
    # Lib menu should have "Cat1" submenu and "Snip3" action
    assert len(lib_menu.actions()) >= 2
    
    cat_action = next(a for a in lib_menu.actions() if a.text() == "Cat1")
    cat_menu = cat_action.menu()
    
    assert len(cat_menu.actions()) == 2
    assert cat_menu.actions()[0].text() == "Snip1"
