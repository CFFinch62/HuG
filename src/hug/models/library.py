"""Snippet library management."""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from hug.models.snippet import Snippet

logger = logging.getLogger(__name__)


@dataclass
class SnippetLibrary:
    name: str
    snippets: list[Snippet]
    description: str = ""
    language: str = ""
    file_extensions: list[str] = field(default_factory=list)
    version: str = "1.0"
    author: str = ""
    source_path: Path | None = None
    
    @classmethod
    def from_json(cls, path: Path) -> "SnippetLibrary":
        """Load library from JSON file."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            
            snippets_data = data.pop("snippets", [])
            snippets = []
            
            library_name = data.get("name", path.stem)
            library_lang = data.get("language", "")
            
            for s_data in snippets_data:
                # Ensure required fields
                if "id" not in s_data or "name" not in s_data or "content" not in s_data:
                    logger.warning(f"Skipping invalid snippet in {path}: {s_data.get('name', 'Unknown')}")
                    continue
                    
                snippet = Snippet(**s_data)
                snippet.library_name = library_name
                snippet.language = library_lang
                snippets.append(snippet)
                
            return cls(
                snippets=snippets,
                source_path=path,
                **data
            )
        except Exception as e:
            logger.error(f"Failed to load library from {path}: {e}")
            raise
        
    def get_categories(self) -> list[str]:
        """Return sorted list of unique categories."""
        return sorted(list(set(s.category for s in self.snippets if s.category)))
        
    def get_snippets_by_category(self, category: str) -> list[Snippet]:
        """Return snippets in given category."""
        return [s for s in self.snippets if s.category == category]


class LibraryManager:
    def __init__(self, library_paths: list[str]):
        # Convert strings to Paths, ignore invalid ones
        self.library_paths = [Path(p) for p in library_paths if p]
        self.libraries: dict[str, SnippetLibrary] = {}
        
    def load_all(self) -> None:
        """Scan library paths and load all JSON files."""
        self.libraries.clear()
        
        for path in self.library_paths:
            if not path.exists():
                logger.warning(f"Library path does not exist: {path}")
                continue
                
            if path.is_file():
                files = [path]
            else:
                files = list(path.glob("**/*.json"))
                
            for file_path in files:
                try:
                    lib = SnippetLibrary.from_json(file_path)
                    self.libraries[lib.name] = lib
                    logger.info(f"Loaded library {lib.name} with {len(lib.snippets)} snippets")
                except Exception:
                    # Already logged in from_json
                    continue
        
    def reload(self) -> None:
        """Clear and reload all libraries."""
        self.load_all()
        
    def get_all_snippets(self) -> list[Snippet]:
        """Return flat list of all snippets."""
        all_snippets = []
        for lib in self.libraries.values():
            all_snippets.extend(lib.snippets)
        return all_snippets
        
    def search(self, query: str) -> list[Snippet]:
        """Search all snippets by query string."""
        results = []
        for snippet in self.get_all_snippets():
            if snippet.matches_filter(query):
                results.append(snippet)
        return results
