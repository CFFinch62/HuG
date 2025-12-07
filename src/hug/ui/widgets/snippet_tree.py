"""Snippet tree widget."""
from typing import cast

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator

from hug.models.library import LibraryManager, SnippetLibrary
from hug.models.snippet import Snippet


class SnippetItem(QTreeWidgetItem):
    """Tree item representing a snippet."""
    def __init__(self, snippet: Snippet):
        super().__init__([snippet.name])
        self.snippet = snippet
        self.setToolTip(0, snippet.description)
        # Store snippet object for retrieval
        self.setData(0, Qt.UserRole, snippet)


class CategoryItem(QTreeWidgetItem):
    """Tree item representing a category."""
    def __init__(self, name: str):
        super().__init__([name])
        self.setExpanded(True)


class LibraryItem(QTreeWidgetItem):
    """Tree item representing a library."""
    def __init__(self, library: SnippetLibrary):
        super().__init__([library.name])
        self.library = library
        self.setExpanded(True)
        font = self.font(0)
        font.setBold(True)
        self.setFont(0, font)


class SnippetTree(QTreeWidget):
    snippet_selected = Signal(Snippet)
    preview_snippet = Signal(object) # object can be Snippet or None
    
    def __init__(self, library_manager: LibraryManager, parent=None):
        super().__init__(parent)
        self.library_manager = library_manager
        self.setHeaderHidden(True)
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        """Configure tree behavior."""
        self.itemActivated.connect(self._on_item_activated)
        self.currentItemChanged.connect(self._on_current_changed)
        
    def refresh(self) -> None:
        """Rebuild tree from libraries."""
        self.clear()
        
        for lib_name, library in self.library_manager.libraries.items():
            lib_item = LibraryItem(library)
            self.addTopLevelItem(lib_item)
            
            categories = library.get_categories()
            
            # Map categories to items
            cat_items = {}
            for cat in categories:
                cat_item = CategoryItem(cat)
                lib_item.addChild(cat_item)
                cat_items[cat] = cat_item
                
            # Add snippets
            for snippet in library.snippets:
                snip_item = SnippetItem(snippet)
                if snippet.category:
                    cat_items[snippet.category].addChild(snip_item)
                else:
                    lib_item.addChild(snip_item)
                    
    def filter(self, query: str) -> None:
        """Filter items by query text."""
        query = query.lower()
        
        # Helper to recursively check and hide items
        # Returns True if item corresponds to query or has visible children
        def check_item(item: QTreeWidgetItem) -> bool:
            if isinstance(item, SnippetItem):
                match = item.snippet.matches_filter(query)
                item.setHidden(not match)
                return match
                
            # For container items (Library/Category), check children
            has_visible_child = False
            for i in range(item.childCount()):
                child = item.child(i)
                if check_item(child):
                    has_visible_child = True
                    
            # If query matches category name itself, maybe show all?
            # For now, simplistic: show if children match
            item.setHidden(not has_visible_child)
            
            # If valid, expand to show matches
            if has_visible_child:
                item.setExpanded(True)
                
            return has_visible_child

        # Run check on top level items
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            check_item(root.child(i))
            
    def _on_item_activated(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle Enter/Double-click."""
        if isinstance(item, SnippetItem):
            self.snippet_selected.emit(item.snippet)
            
    def _on_current_changed(self, current: QTreeWidgetItem, previous: QTreeWidgetItem) -> None:
        """Handle selection change (for preview)."""
        if isinstance(current, SnippetItem):
            self.preview_snippet.emit(current.snippet)
        else:
            self.preview_snippet.emit(None)

    def select_first_visible(self) -> None:
        """Select the first visible snippet item."""
        it = QTreeWidgetItemIterator(self)
        while it.value():
            item = it.value()
            if isinstance(item, SnippetItem) and not item.isHidden():
                self.setCurrentItem(item)
                return
            it += 1
