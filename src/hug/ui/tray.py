"""System Tray implementation."""
import logging
from typing import cast

from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from hug.models.library import LibraryManager, SnippetLibrary, Snippet
from hug.models.snippet import Snippet

logger = logging.getLogger(__name__)


class SystemTray(QSystemTrayIcon):
    snippet_selected = Signal(Snippet)
    quit_requested = Signal()
    settings_requested = Signal()
    menu_about_to_show = Signal()  # Emitted before menu is shown

    def __init__(self, library_manager: LibraryManager, icon_path: str, parent=None):
        super().__init__(parent)
        self.library_manager = library_manager

        # Set icon
        icon = QIcon(icon_path)
        if icon.isNull():
            logger.warning(f"Failed to load icon from {icon_path}")
            # Fallback or empty icon
        self.setIcon(icon)
        self.setToolTip("HuG Snippet Manager")

        # Build menu
        self.menu = QMenu()
        self._build_menu()
        self.setContextMenu(self.menu)

        # Connect menu aboutToShow signal
        self.menu.aboutToShow.connect(self._on_menu_about_to_show)

        self.show()

    def _on_menu_about_to_show(self) -> None:
        """Handle menu about to be shown."""
        self.menu_about_to_show.emit()
        
    def _build_menu(self) -> None:
        """Build context menu from current libraries, grouped by source folder."""
        self.menu.clear()

        # 1. Libraries, grouped into labeled sections by the folder they were loaded from
        grouped = self.library_manager.get_libraries_by_folder()
        for i, (folder, libraries) in enumerate(grouped.items()):
            if folder:
                self.menu.addSection(folder.replace("_", " ").replace("-", " ").title())
            elif i > 0:
                self.menu.addSeparator()
            for library in libraries:
                lib_menu = self.menu.addMenu(library.name)
                self._populate_library_menu(lib_menu, library)

        self.menu.addSeparator()

        # 2. Settings action - connect to signal so it survives rebuild
        settings_action = self.menu.addAction("Settings")
        settings_action.triggered.connect(self.settings_requested.emit)

        # 3. Quit action
        quit_action = self.menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_requested.emit)
        
    def _populate_library_menu(self, menu: QMenu, library: SnippetLibrary) -> None:
        """Populate a library submenu, grouping by category."""
        categories = library.get_categories()
        
        # Submenus for categories
        for category in categories:
            cat_menu = menu.addMenu(category)
            snippets = library.get_snippets_by_category(category)
            self._add_snippets_to_menu(cat_menu, snippets)
            
        # Uncategorized snippets (those with empty category)
        uncategorized = [s for s in library.snippets if not s.category]
        if uncategorized:
            if categories:
                menu.addSeparator()
            self._add_snippets_to_menu(menu, uncategorized)
            
    def _add_snippets_to_menu(self, menu: QMenu, snippets: list[Snippet]) -> None:
        """Add action items for snippets to a menu."""
        for snippet in snippets:
            action = menu.addAction(snippet.name)
            # Capture only the ID/library name (default params bind the loop
            # variable). The snippet itself is re-resolved at click time so
            # edits made after the menu was built are always reflected.
            action.triggered.connect(
                lambda checked=False, sid=snippet.id, lib=snippet.library_name: self._on_snippet_triggered(sid, lib)
            )
            action.setToolTip(snippet.description)

    def _on_snippet_triggered(self, snippet_id: str, library_name: str) -> None:
        """Handle snippet selection, looking up the current snippet data."""
        snippet = self.library_manager.get_snippet(snippet_id, library_name)
        if snippet is None:
            logger.warning(f"Snippet '{snippet_id}' in '{library_name}' no longer exists")
            return
        logger.info(f"Snippet selected: {snippet.name}")
        self.snippet_selected.emit(snippet)
        
    def rebuild_menu(self) -> None:
        """Rebuild menu (e.g. after reload)."""
        self._build_menu()
