"""Settings dialog."""
import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QFormLayout, 
    QLineEdit, QCheckBox, QSpinBox, QDialogButtonBox, QLabel
)

from hug.config import Config, HotkeyConfig, PaletteConfig

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    config_changed = Signal(Config)
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("HuG Settings")
        self.resize(500, 400)
        self.config = config
        
        # Working copy of config would be better, but direct edit for now 
        # (simplified for this phase)
        
        self._setup_ui()
        
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "General")
        tabs.addTab(self._create_appearance_tab(), "Appearance")
        tabs.addTab(self._create_libraries_tab(), "Libraries")
        
        layout.addWidget(tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _create_general_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Hotkey
        self.hotkey_edit = QLineEdit(self.config.hotkey.summon_palette)
        layout.addRow("Summon Hotkey:", self.hotkey_edit)
        
        # Clipboard
        self.restore_clipboard = QCheckBox()
        self.restore_clipboard.setChecked(self.config.clipboard.restore_previous)
        layout.addRow("Restore Clipboard:", self.restore_clipboard)
        
        return widget
        
    def _create_appearance_tab(self) -> QWidget:
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Palette Size
        self.width_spin = QSpinBox()
        self.width_spin.setRange(200, 1000)
        self.width_spin.setValue(self.config.palette.width)
        layout.addRow("Palette Width:", self.width_spin)
        
        self.height_spin = QSpinBox()
        self.height_spin.setRange(200, 1000)
        self.height_spin.setValue(self.config.palette.height)
        layout.addRow("Palette Height:", self.height_spin)
        
        return widget

    def _create_libraries_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Library Paths (one per line):"))
        # Using multiline edit for simplicity
        from PySide6.QtWidgets import QTextEdit
        self.paths_edit = QTextEdit()
        self.paths_edit.setPlainText("\n".join(self.config.library_paths))
        layout.addWidget(self.paths_edit)
        
        return widget
        
    def accept(self) -> None:
        """Save changes back to config object."""
        # Update Config Object
        self.config.hotkey.summon_palette = self.hotkey_edit.text()
        self.config.clipboard.restore_previous = self.restore_clipboard.isChecked()
        self.config.palette.width = self.width_spin.value()
        self.config.palette.height = self.height_spin.value()
        
        paths = self.paths_edit.toPlainText().split('\n')
        self.config.library_paths = [p.strip() for p in paths if p.strip()]
        
        self.config_changed.emit(self.config)
        super().accept()
