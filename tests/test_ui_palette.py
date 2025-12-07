"""Tests for Palette logic."""
from unittest.mock import MagicMock
from PySide6.QtCore import Qt

from hug.ui.palette import FloatingPalette
from hug.config import PaletteConfig
from hug.models.library import LibraryManager, SnippetLibrary, Snippet


def test_palette_search_filtering(qtbot):
    # Mock Manager
    manager = MagicMock(spec=LibraryManager)
    
    snippets = [
        Snippet(id="1", name="Python Loop", content="for i in range(10):", category="Code"),
        Snippet(id="2", name="Ruby Loop", content="10.times do", category="Code"),
    ]
    lib = SnippetLibrary(name="CodeLib", snippets=snippets)
    manager.libraries = {"CodeLib": lib}
    
    # Init Palette
    config = PaletteConfig()
    palette = FloatingPalette(manager, config)
    qtbot.addWidget(palette)
    
    # Initial state: 2 snippets visible (nested in library/category)
    # We can check the tree model directly
    root = palette.tree.invisibleRootItem()
    assert root.childCount() == 1 # CodeLib
    
    # Filter for "Python"
    qtbot.keyClicks(palette.search_box, "Python")
    
    # Check visibility
    # We need to traverse to find the items
    lib_item = root.child(0)
    cat_item = lib_item.child(0) # Code
    
    # There should only be one visible child under category now
    visible_count = 0
    for i in range(cat_item.childCount()):
        if not cat_item.child(i).isHidden():
            visible_count += 1
            
    assert visible_count == 1
    assert "Python" in cat_item.child(0).text(0)
