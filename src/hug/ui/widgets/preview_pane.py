"""Preview pane widget."""
from PySide6.QtWidgets import QTextEdit
from PySide6.QtGui import QFont

from hug.models.snippet import Snippet

class PreviewPane(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        # Use a monospace font
        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)
        
    def show_snippet(self, snippet: Snippet | None) -> None:
        """Display snippet content."""
        if not snippet:
            self.clear()
            return
            
        # TODO: Add syntax highlighting based on snippet.language
        self.setPlainText(snippet.content)
