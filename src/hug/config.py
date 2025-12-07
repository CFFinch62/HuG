"""Configuration management for HuG."""
import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HotkeyConfig:
    summon_palette: str = "Ctrl+Shift+Space"


@dataclass
class PaletteConfig:
    enabled: bool = True
    position: str = "remember"  # "remember", "cursor", "fixed"
    width: int = 350
    height: int = 450
    x: int | None = None
    y: int | None = None
    hide_on_focus_loss: bool = True
    hide_on_selection: bool = True
    show_preview: bool = True


@dataclass
class ClipboardConfig:
    restore_previous: bool = True
    restore_delay_ms: int = 100


@dataclass
class AppearanceConfig:
    theme: str = "system"  # "system", "light", "dark"
    font_family: str = "monospace"
    font_size: int = 12


@dataclass
class StartupConfig:
    start_minimized: bool = True
    start_on_login: bool = False


@dataclass
class Config:
    version: str = "1.0"
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    palette: PaletteConfig = field(default_factory=PaletteConfig)
    clipboard: ClipboardConfig = field(default_factory=ClipboardConfig)
    appearance: AppearanceConfig = field(default_factory=AppearanceConfig)
    startup: StartupConfig = field(default_factory=StartupConfig)
    library_paths: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> "Config":
        """Load config from JSON file, applying defaults."""
        if not path.exists():
            logger.info(f"Config file not found at {path}, using defaults")
            return cls(library_paths=cls.get_default_library_paths())

        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            # Helper to safely load nested dataclasses
            def load_nested(config_cls, data_dict):
                return config_cls(**{k: v for k, v in data_dict.items() if k in config_cls.__annotations__})

            # Use defaults if library_paths is empty or not present
            library_paths = data.get("library_paths", [])
            if not library_paths:
                library_paths = cls.get_default_library_paths()

            return cls(
                version=data.get("version", "1.0"),
                hotkey=load_nested(HotkeyConfig, data.get("hotkey", {})),
                palette=load_nested(PaletteConfig, data.get("palette", {})),
                clipboard=load_nested(ClipboardConfig, data.get("clipboard", {})),
                appearance=load_nested(AppearanceConfig, data.get("appearance", {})),
                startup=load_nested(StartupConfig, data.get("startup", {})),
                library_paths=library_paths,
            )
        except Exception as e:
            logger.error(f"Failed to load config from {path}: {e}")
            return cls(library_paths=cls.get_default_library_paths())

    def save(self, path: Path) -> None:
        """Save current config to JSON file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(asdict(self), f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save config to {path}: {e}")

    @staticmethod
    def get_default_paths() -> Path:
        """Return platform-appropriate config directory."""
        if sys.platform == "win32":
            return Path(os.environ["APPDATA"]) / "HuG"
        elif sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "HuG"
        else:
            # XDG based
            return Path.home() / ".config" / "hug"

    @staticmethod
    def get_default_library_paths() -> list[str]:
        """Return default snippet library paths."""
        # For development/portable use, look relative to executable/script
        # config.py is at src/hug/config.py, so go up 3 levels to reach project root
        base_dir = Path(__file__).resolve().parent.parent.parent
        snippets_dir = base_dir / "snippets"
        if snippets_dir.exists():
            return [str(snippets_dir)]
        return []
