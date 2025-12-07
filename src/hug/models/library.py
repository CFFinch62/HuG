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

    def to_dict(self) -> dict:
        """Convert library to dictionary for JSON serialization."""
        data = {
            "name": self.name,
            "snippets": [s.to_dict() for s in self.snippets],
        }
        # Only include optional fields if they have values
        if self.description:
            data["description"] = self.description
        if self.language:
            data["language"] = self.language
        if self.file_extensions:
            data["file_extensions"] = self.file_extensions
        if self.version:
            data["version"] = self.version
        if self.author:
            data["author"] = self.author
        return data

    def save(self) -> bool:
        """Save library back to its source JSON file."""
        if not self.source_path:
            logger.error("Cannot save library: no source path")
            return False

        try:
            data = self.to_dict()
            with open(self.source_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved library '{self.name}' to {self.source_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save library to {self.source_path}: {e}")
            return False

    def add_snippet(self, snippet: Snippet) -> None:
        """Add a new snippet to the library."""
        snippet.library_name = self.name
        snippet.language = self.language
        self.snippets.append(snippet)

    def update_snippet(self, snippet: Snippet) -> bool:
        """Update an existing snippet by ID. Returns True if found and updated."""
        for i, existing in enumerate(self.snippets):
            if existing.id == snippet.id:
                snippet.library_name = self.name
                snippet.language = self.language
                self.snippets[i] = snippet
                return True
        return False

    def remove_snippet(self, snippet_id: str) -> bool:
        """Remove a snippet by ID. Returns True if found and removed."""
        for i, snippet in enumerate(self.snippets):
            if snippet.id == snippet_id:
                del self.snippets[i]
                return True
        return False


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

    def save_snippet(self, snippet: Snippet, library_name: str) -> bool:
        """
        Save a snippet to the specified library.
        If snippet.id exists in the library, it updates; otherwise, it adds.
        If the library doesn't exist and name starts with '(No libraries', creates 'My Snippets'.
        Returns True on success.
        """
        library = self.libraries.get(library_name)

        # Handle case where no libraries exist
        if not library:
            if library_name.startswith("(No libraries"):
                # Create default library
                library = self.create_library("My Snippets", "User-created snippets")
                if not library:
                    return False
            else:
                logger.error(f"Library '{library_name}' not found")
                return False

        # Check if updating existing or adding new
        if library.update_snippet(snippet):
            logger.info(f"Updated snippet '{snippet.name}' in '{library.name}'")
        else:
            library.add_snippet(snippet)
            logger.info(f"Added snippet '{snippet.name}' to '{library.name}'")

        return library.save()

    def delete_snippet(self, snippet_id: str, library_name: str) -> bool:
        """Delete a snippet from the specified library."""
        library = self.libraries.get(library_name)
        if not library:
            logger.error(f"Library '{library_name}' not found")
            return False

        if library.remove_snippet(snippet_id):
            logger.info(f"Removed snippet '{snippet_id}' from '{library_name}'")
            return library.save()

        logger.warning(f"Snippet '{snippet_id}' not found in '{library_name}'")
        return False

    def create_library(self, name: str, description: str = "") -> SnippetLibrary | None:
        """
        Create a new empty library in the first library path.
        Returns the created library or None on failure.
        """
        if not self.library_paths:
            logger.error("No library paths configured")
            return None

        # Use first path
        base_path = self.library_paths[0]
        if not base_path.exists():
            try:
                base_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create library path: {e}")
                return None

        # Create filename from name
        filename = name.lower().replace(" ", "-") + ".json"
        file_path = base_path / filename

        if file_path.exists():
            logger.error(f"Library file already exists: {file_path}")
            return None

        library = SnippetLibrary(
            name=name,
            snippets=[],
            description=description,
            source_path=file_path,
        )

        if library.save():
            self.libraries[name] = library
            logger.info(f"Created new library '{name}' at {file_path}")
            return library

        return None
