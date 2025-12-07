"""Floating palette window."""
import logging
from typing import cast

from PySide6.QtCore import Qt, Signal, QEvent, QObject
from PySide6.QtGui import QKeyEvent, QFocusEvent
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QSplitter,
    QPushButton, QMessageBox
)

from hug.config import PaletteConfig
from hug.models.library import LibraryManager
from hug.models.snippet import Snippet
from hug.ui.widgets.snippet_tree import SnippetTree
from hug.ui.widgets.preview_pane import PreviewPane

logger = logging.getLogger(__name__)


class FloatingPalette(QWidget):
    snippet_selected = Signal(Snippet)
    closed = Signal()
    
    def __init__(self, library_manager: LibraryManager, config: PaletteConfig):
        super().__init__()
        self.library_manager = library_manager
        self.config = config
        
        self._setup_ui()
        self._setup_window_flags()
        
    def _setup_ui(self) -> None:
        """Create layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search row with buttons
        search_row = QHBoxLayout()

        # Search Box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search snippets...")
        self.search_box.textChanged.connect(self._on_search_changed)
        search_row.addWidget(self.search_box)

        # New Snippet button
        self.new_btn = QPushButton("+")
        self.new_btn.setToolTip("Create new snippet")
        self.new_btn.setFixedWidth(30)
        self.new_btn.clicked.connect(self._on_new_snippet)
        search_row.addWidget(self.new_btn)

        # Clipboard button
        self.clipboard_btn = QPushButton("📋")
        self.clipboard_btn.setToolTip("Create snippet from clipboard")
        self.clipboard_btn.setFixedWidth(30)
        self.clipboard_btn.clicked.connect(self._on_new_from_clipboard)
        search_row.addWidget(self.clipboard_btn)

        layout.addLayout(search_row)

        # Splitter for Tree and Preview
        splitter = QSplitter(Qt.Vertical)

        # Tree
        self.tree = SnippetTree(self.library_manager)
        self.tree.snippet_selected.connect(self._on_snippet_selected)
        self.tree.preview_snippet.connect(self._on_preview_requested)
        self.tree.edit_snippet.connect(self._on_edit_snippet)
        self.tree.delete_snippet.connect(self._on_delete_snippet)
        splitter.addWidget(self.tree)

        # Preview
        if self.config.show_preview:
            self.preview = PreviewPane()
            splitter.addWidget(self.preview)
            # Set initial sizes (70% tree, 30% preview)
            splitter.setSizes([int(self.config.height * 0.7), int(self.config.height * 0.3)])

        layout.addWidget(splitter)

        # Initial data load
        self.refresh()

        # Install event filter on search box to handle arrow keys
        self.search_box.installEventFilter(self)
        
    def _setup_window_flags(self) -> None:
        """Configure frameless, always-on-top."""
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.resize(self.config.width, self.config.height)
        
    def show_at_position(self) -> None:
        """Show window at configured position."""
        self.search_box.clear()
        self.search_box.setFocus()
        self.tree.select_first_visible()
        
        # Simple centering for now if no specific logic
        # TODO: Implement "cursor" or "remember" logic
        if self.config.position == "cursor":
            from PySide6.QtGui import QCursor
            pos = QCursor.pos()
            self.move(pos)
        else:
             # Center on screen
            from PySide6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)
            
        self.show()
        self.activateWindow()
        
    def refresh(self) -> None:
        """Rebuild tree."""
        self.tree.refresh()
        
    def _on_search_changed(self, text: str) -> None:
        """Filter tree."""
        self.tree.filter(text)
        self.tree.select_first_visible()
        
    def _on_snippet_selected(self, snippet: Snippet) -> None:
        """Propagate signal and close."""
        self.snippet_selected.emit(snippet)
        if self.config.hide_on_selection:
            self.hide()
            self.closed.emit()
            
    def _on_preview_requested(self, snippet: Snippet | None) -> None:
        if hasattr(self, 'preview'):
            self.preview.show_snippet(snippet)
            
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Handle global keys."""
        if event.key() == Qt.Key_Escape:
            self.hide()
            self.closed.emit()
        else:
            super().keyPressEvent(event)
            
    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """Redirect arrow keys from search box to tree."""
        if obj == self.search_box and event.type() == QEvent.KeyPress:
            key = cast(QKeyEvent, event).key()
            if key in (Qt.Key_Up, Qt.Key_Down, Qt.Key_PageUp, Qt.Key_PageDown):
                # Pass to tree
                self.tree.keyPressEvent(event)
                return True
            if key == Qt.Key_Enter or key == Qt.Key_Return:
                # Select current item in tree
                item = self.tree.currentItem()
                if item:
                    self.tree._on_item_activated(item, 0)
                return True
                
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Hide on focus loss."""
        if self.config.hide_on_focus_loss:
            self.hide()

    def _on_new_snippet(self) -> None:
        """Open editor dialog for creating a new snippet."""
        from hug.ui.snippet_editor import SnippetEditorDialog

        dialog = SnippetEditorDialog(self.library_manager, parent=self)
        dialog.snippet_saved.connect(self._save_snippet)
        dialog.exec()

    def _on_new_from_clipboard(self) -> None:
        """Create a new snippet with content from clipboard."""
        from PySide6.QtWidgets import QApplication
        from hug.ui.snippet_editor import SnippetEditorDialog

        clipboard = QApplication.clipboard()
        content = clipboard.text()

        if not content:
            QMessageBox.information(
                self, "Clipboard Empty",
                "There is no text in the clipboard to create a snippet from."
            )
            return

        dialog = SnippetEditorDialog(
            self.library_manager,
            initial_content=content,
            parent=self
        )
        dialog.snippet_saved.connect(self._save_snippet)
        dialog.exec()

    def _on_edit_snippet(self, snippet: Snippet) -> None:
        """Open editor dialog to edit an existing snippet."""
        from hug.ui.snippet_editor import SnippetEditorDialog

        dialog = SnippetEditorDialog(self.library_manager, snippet=snippet, parent=self)
        dialog.snippet_saved.connect(self._save_snippet)
        dialog.exec()

    def _on_delete_snippet(self, snippet: Snippet) -> None:
        """Delete a snippet after confirmation."""
        reply = QMessageBox.question(
            self, "Delete Snippet",
            f"Are you sure you want to delete '{snippet.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.library_manager.delete_snippet(snippet.id, snippet.library_name)
            if success:
                self.refresh()
            else:
                QMessageBox.warning(
                    self, "Error",
                    f"Failed to delete snippet '{snippet.name}'."
                )

    def _save_snippet(self, snippet: Snippet, library_name: str) -> None:
        """Save snippet to library and refresh the tree."""
        success = self.library_manager.save_snippet(snippet, library_name)
        if success:
            self.refresh()
        else:
            QMessageBox.warning(
                self, "Error",
                f"Failed to save snippet '{snippet.name}'."
            )
            self.closed.emit()
        super().focusOutEvent(event)
