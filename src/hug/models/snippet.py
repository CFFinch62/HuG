"""Snippet data model."""
from dataclasses import dataclass, field


@dataclass
class Snippet:
    id: str
    name: str
    content: str
    description: str = ""
    category: str = ""
    tags: list[str] = field(default_factory=list)

    # Back-reference to containing library (set during loading)
    library_name: str = ""
    language: str = ""

    def matches_filter(self, query: str) -> bool:
        """Check if snippet matches search query."""
        if not query:
            return True

        query = query.lower()
        return (
            query in self.name.lower() or
            query in self.description.lower() or
            any(query in tag.lower() for tag in self.tags)
        )

    def to_dict(self) -> dict:
        """Convert snippet to dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "name": self.name,
            "content": self.content,
        }
        # Only include optional fields if they have values
        if self.description:
            data["description"] = self.description
        if self.category:
            data["category"] = self.category
        if self.tags:
            data["tags"] = self.tags
        return data
