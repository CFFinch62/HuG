"""Tests for configuration module."""
import json
from pathlib import Path

from hug.config import Config, HotkeyConfig, PaletteConfig


def test_config_defaults():
    config = Config.load(Path("non_existent.json"))
    assert config.version == "1.0"
    assert config.hotkey.summon_palette == "Ctrl+Shift+Space"
    assert config.palette.width == 350


def test_config_save_load(tmp_path):
    config_path = tmp_path / "config.json"
    
    config = Config()
    config.hotkey.summon_palette = "Ctrl+D"
    config.palette.enabled = False
    
    config.save(config_path)
    
    assert config_path.exists()
    
    loaded = Config.load(config_path)
    assert loaded.hotkey.summon_palette == "Ctrl+D"
    assert loaded.palette.enabled is False
    assert loaded.clipboard.restore_previous is True  # default
