"""Snippet editor dialog for creating and editing snippets."""
import logging
import re
import uuid

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QPushButton,
    QDialogButtonBox, QLabel, QMessageBox, QWidget
)

from hug.models.snippet import Snippet
from hug.models.library import LibraryManager, SnippetLibrary

logger = logging.getLogger(__name__)


def generate_snippet_id(name: str) -> str:
    """Generate a snake_case ID from a snippet name."""
    # Convert to lowercase
    id_str = name.lower()
    # Replace spaces and special chars with underscores
    id_str = re.sub(r'[^a-z0-9]+', '_', id_str)
    # Remove leading/trailing underscores
    id_str = id_str.strip('_')
    # Ensure it starts with a letter
    if id_str and not id_str[0].isalpha():
        id_str = 'snippet_' + id_str
    # Add short unique suffix to avoid collisions
    short_uuid = uuid.uuid4().hex[:6]
    return f"{id_str}_{short_uuid}" if id_str else f"snippet_{short_uuid}"


class SnippetEditorDialog(QDialog):
    """Dialog for creating or editing a snippet."""
    
    snippet_saved = Signal(Snippet, str)  # Emits (snippet, library_name)
    
    def __init__(
        self, 
        library_manager: LibraryManager,
        snippet: Snippet | None = None,
        initial_content: str = "",
        parent=None
    ):
        super().__init__(parent)
        self.library_manager = library_manager
        self.editing_snippet = snippet
        self.initial_content = initial_content
        
        self.setWindowTitle("Edit Snippet" if snippet else "New Snippet")
        self.resize(500, 450)
        self._setup_ui()
        
        if snippet:
            self._populate_from_snippet(snippet)
        elif initial_content:
            self.content_edit.setPlainText(initial_content)
    
    def _setup_ui(self) -> None:
        """Create the form layout."""
        layout = QVBoxLayout(self)
        
        form = QFormLayout()
        
        # Library selector
        self.library_combo = QComboBox()
        self._populate_libraries()
        form.addRow("Library:", self.library_combo)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., For Loop")
        form.addRow("Name:*", self.name_edit)
        
        # Category (with autocomplete from existing categories)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self._populate_categories()
        self.category_combo.setCurrentText("")
        form.addRow("Category:", self.category_combo)
        
        # Description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Brief description (optional)")
        form.addRow("Description:", self.description_edit)
        
        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("comma, separated, tags")
        form.addRow("Tags:", self.tags_edit)
        
        layout.addLayout(form)
        
        # Content (large text area)
        layout.addWidget(QLabel("Content:*"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Paste or type your snippet content here...")
        self.content_edit.setMinimumHeight(150)
        layout.addWidget(self.content_edit)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self._on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _populate_libraries(self) -> None:
        """Fill library dropdown with available libraries."""
        for lib_name in self.library_manager.libraries.keys():
            self.library_combo.addItem(lib_name)

        # If no libraries exist, show a message
        if not self.library_manager.libraries:
            self.library_combo.addItem("(No libraries - will create 'My Snippets')")

        # If editing, select the snippet's library
        if self.editing_snippet and self.editing_snippet.library_name:
            idx = self.library_combo.findText(self.editing_snippet.library_name)
            if idx >= 0:
                self.library_combo.setCurrentIndex(idx)
    
    def _populate_categories(self) -> None:
        """Fill category dropdown with existing categories."""
        categories = set()
        for lib in self.library_manager.libraries.values():
            categories.update(lib.get_categories())
        
        self.category_combo.addItems(sorted(categories))
    
    def _populate_from_snippet(self, snippet: Snippet) -> None:
        """Fill form fields from an existing snippet."""
        self.name_edit.setText(snippet.name)
        self.category_combo.setCurrentText(snippet.category)
        self.description_edit.setText(snippet.description)
        self.tags_edit.setText(", ".join(snippet.tags))
        self.content_edit.setPlainText(snippet.content)
    
    def _on_save(self) -> None:
        """Validate and save the snippet."""
        # Validation
        name = self.name_edit.text().strip()
        content = self.content_edit.toPlainText()
        
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required.")
            self.name_edit.setFocus()
            return
        
        if not content:
            QMessageBox.warning(self, "Validation Error", "Content is required.")
            self.content_edit.setFocus()
            return
        
        library_name = self.library_combo.currentText()
        if not library_name:
            QMessageBox.warning(self, "Validation Error", "Please select a library.")
            return
        
        # Build snippet
        snippet_id = self.editing_snippet.id if self.editing_snippet else generate_snippet_id(name)
        
        tags_text = self.tags_edit.text()
        tags = [t.strip() for t in tags_text.split(",") if t.strip()] if tags_text else []
        
        snippet = Snippet(
            id=snippet_id,
            name=name,
            content=content,
            description=self.description_edit.text().strip(),
            category=self.category_combo.currentText().strip(),
            tags=tags,
            library_name=library_name,
        )
        
        self.snippet_saved.emit(snippet, library_name)
        self.accept()

