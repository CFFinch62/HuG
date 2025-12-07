"""Tests for data models."""
import json
from pathlib import Path

from hug.models.snippet import Snippet
from hug.models.library import SnippetLibrary, LibraryManager


def test_snippet_matching():
    s = Snippet(
        id="1", 
        name="Test Snippet", 
        content="print('hello')",
        tags=["python", "test"]
    )
    
    assert s.matches_filter("Test")
    assert s.matches_filter("test")
    assert s.matches_filter("python")
    assert not s.matches_filter("ruby")


def test_library_loading(tmp_path):
    lib_file = tmp_path / "test.json"
    data = {
        "name": "Test Lib",
        "snippets": [
            {
                "id": "1",
                "name": "Snippet 1",
                "content": "code1",
                "category": "Cat A"
            },
            {
                "id": "2",
                "name": "Snippet 2",
                "content": "code2",
                "category": "Cat B"
            }
        ]
    }
    
    with open(lib_file, "w") as f:
        json.dump(data, f)
        
    lib = SnippetLibrary.from_json(lib_file)
    assert lib.name == "Test Lib"
    assert len(lib.snippets) == 2
    assert "Cat A" in lib.get_categories()
