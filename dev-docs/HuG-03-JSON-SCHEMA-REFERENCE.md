# JSON Schema Reference: HuG Snippet Library Format

**Version:** 1.0  
**Date:** December 2024

---

## 1. Overview

This document defines the JSON schema for snippet library files used by HuG. These files are the primary data format for storing and exchanging text snippets. The format is designed to be:

- Human-readable and editable
- Parseable by any JSON-compliant tool
- Extensible for future features
- Usable by multiple applications (HuG, Just Code plugin, etc.)

---

## 2. File Organization

### 2.1 Directory Structure

```
snippets/
├── general/           # Non-code text snippets
│   ├── business.json
│   ├── email.json
│   └── common.json
└── code/              # Programming language snippets
    ├── python.json
    ├── ruby.json
    ├── javascript.json
    ├── html.json
    ├── css.json
    └── racket.json
```

### 2.2 File Naming Convention

- Use lowercase names
- Use hyphens for multi-word names (e.g., `visual-basic.json`)
- One library per file
- File name should match the language or category name

---

## 3. Schema Definition

### 3.1 Complete JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://fragillidae.software/schemas/snippet-library-v1.json",
  "title": "Snippet Library",
  "description": "A collection of text snippets for insertion",
  "type": "object",
  "required": ["name", "snippets"],
  "properties": {
    "name": {
      "type": "string",
      "description": "Display name for the library",
      "minLength": 1,
      "maxLength": 100
    },
    "description": {
      "type": "string",
      "description": "Brief description of library contents",
      "maxLength": 500
    },
    "language": {
      "type": "string",
      "description": "Programming language identifier (use 'text' for general snippets)",
      "pattern": "^[a-z][a-z0-9_-]*$"
    },
    "file_extensions": {
      "type": "array",
      "description": "File extensions associated with this language",
      "items": {
        "type": "string",
        "pattern": "^\\.[a-z0-9]+$"
      }
    },
    "version": {
      "type": "string",
      "description": "Semantic version of this library",
      "pattern": "^\\d+\\.\\d+(\\.\\d+)?$"
    },
    "author": {
      "type": "string",
      "description": "Library author or maintainer",
      "maxLength": 100
    },
    "snippets": {
      "type": "array",
      "description": "Array of snippet definitions",
      "items": {
        "$ref": "#/definitions/snippet"
      },
      "minItems": 1
    }
  },
  "definitions": {
    "snippet": {
      "type": "object",
      "required": ["id", "name", "content"],
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier within this library",
          "pattern": "^[a-z][a-z0-9_]*$",
          "minLength": 1,
          "maxLength": 50
        },
        "name": {
          "type": "string",
          "description": "Human-readable display name",
          "minLength": 1,
          "maxLength": 100
        },
        "description": {
          "type": "string",
          "description": "Explanation of the snippet's purpose",
          "maxLength": 500
        },
        "category": {
          "type": "string",
          "description": "Subcategory for grouping within library",
          "pattern": "^[a-z][a-z0-9_-]*$",
          "maxLength": 50
        },
        "tags": {
          "type": "array",
          "description": "Searchable keywords",
          "items": {
            "type": "string",
            "maxLength": 30
          },
          "maxItems": 10
        },
        "content": {
          "type": "string",
          "description": "The snippet text to insert",
          "minLength": 1
        }
      }
    }
  }
}
```

---

## 4. Field Reference

### 4.1 Library-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | string | **Yes** | — | Display name shown in menus and palette |
| `description` | string | No | `""` | Brief explanation of what snippets this library contains |
| `language` | string | No | `""` | Language identifier; use `"text"` for non-code snippets |
| `file_extensions` | array | No | `[]` | File extensions (e.g., `[".py", ".pyw"]`) for context filtering |
| `version` | string | No | `"1.0"` | Semantic version for tracking library updates |
| `author` | string | No | `""` | Creator or maintainer attribution |
| `snippets` | array | **Yes** | — | Array of snippet objects |

### 4.2 Snippet-Level Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `id` | string | **Yes** | — | Unique identifier (lowercase, underscores only) |
| `name` | string | **Yes** | — | Display name shown to user |
| `content` | string | **Yes** | — | The actual text to insert |
| `description` | string | No | `""` | Helpful explanation of when/how to use |
| `category` | string | No | `""` | Grouping within library (e.g., "loops", "functions") |
| `tags` | array | No | `[]` | Keywords for search/filtering |

---

## 5. Content Encoding

### 5.1 Escape Sequences

Snippet content is a JSON string and must use JSON escape sequences:

| Character | Escape | Example |
|-----------|--------|---------|
| Newline | `\n` | `"line1\nline2"` |
| Tab | `\t` | `"indented\ttext"` |
| Backslash | `\\` | `"path\\to\\file"` |
| Double quote | `\"` | `"say \"hello\""` |
| Unicode | `\uXXXX` | `"\u00A9"` for © |

### 5.2 Indentation in Content

For code snippets, use actual characters (escaped as needed), not spaces-for-tabs:

```json
{
  "content": "def function_name():\n\t\"\"\"Docstring.\"\"\"\n\tpass"
}
```

If spaces are preferred for indentation, use literal spaces:

```json
{
  "content": "def function_name():\n    \"\"\"Docstring.\"\"\"\n    pass"
}
```

---

## 6. Complete Examples

### 6.1 Python Code Library

```json
{
  "name": "Python Snippets",
  "description": "Common Python code structures for beginners",
  "language": "python",
  "file_extensions": [".py", ".pyw"],
  "version": "1.0",
  "author": "Fragillidae Software",
  "snippets": [
    {
      "id": "for_loop",
      "name": "For Loop",
      "description": "Iterate over a sequence",
      "category": "loops",
      "tags": ["iteration", "loop", "sequence", "for"],
      "content": "for item in collection:\n    # process item\n    pass"
    },
    {
      "id": "for_range",
      "name": "For Loop (Range)",
      "description": "Iterate a specific number of times",
      "category": "loops",
      "tags": ["iteration", "loop", "range", "counter"],
      "content": "for i in range(count):\n    # iteration i\n    pass"
    },
    {
      "id": "while_loop",
      "name": "While Loop",
      "description": "Loop while condition is true",
      "category": "loops",
      "tags": ["iteration", "loop", "while", "condition"],
      "content": "while condition:\n    # loop body\n    pass"
    },
    {
      "id": "function_def",
      "name": "Function Definition",
      "description": "Define a new function with docstring",
      "category": "functions",
      "tags": ["function", "def", "definition"],
      "content": "def function_name(parameters):\n    \"\"\"Describe what the function does.\"\"\"\n    pass"
    },
    {
      "id": "class_basic",
      "name": "Class Definition",
      "description": "Basic class with constructor",
      "category": "classes",
      "tags": ["class", "oop", "init", "constructor"],
      "content": "class ClassName:\n    \"\"\"Describe the class.\"\"\"\n    \n    def __init__(self, parameters):\n        \"\"\"Initialize the instance.\"\"\"\n        pass"
    },
    {
      "id": "try_except",
      "name": "Try/Except Block",
      "description": "Handle exceptions",
      "category": "error_handling",
      "tags": ["try", "except", "error", "exception"],
      "content": "try:\n    # code that might raise an exception\n    pass\nexcept ExceptionType as e:\n    # handle the exception\n    pass"
    },
    {
      "id": "list_comprehension",
      "name": "List Comprehension",
      "description": "Create a list from an iterable",
      "category": "comprehensions",
      "tags": ["list", "comprehension", "transform"],
      "content": "result = [expression for item in iterable]"
    },
    {
      "id": "with_open",
      "name": "Open File",
      "description": "Open a file safely",
      "category": "context_managers",
      "tags": ["file", "open", "read", "write"],
      "content": "with open(\"filename.txt\", \"r\") as f:\n    content = f.read()"
    },
    {
      "id": "main_guard",
      "name": "Main Guard",
      "description": "Only run when executed directly",
      "category": "structure",
      "tags": ["main", "guard", "entry", "script"],
      "content": "if __name__ == \"__main__\":\n    main()"
    }
  ]
}
```

### 6.2 Ruby Code Library

```json
{
  "name": "Ruby Snippets",
  "description": "Common Ruby code structures",
  "language": "ruby",
  "file_extensions": [".rb", ".rake"],
  "version": "1.0",
  "author": "Fragillidae Software",
  "snippets": [
    {
      "id": "each_loop",
      "name": "Each Loop",
      "description": "Iterate over a collection",
      "category": "loops",
      "tags": ["each", "loop", "iteration"],
      "content": "collection.each do |item|\n  # process item\nend"
    },
    {
      "id": "method_def",
      "name": "Method Definition",
      "description": "Define a method",
      "category": "methods",
      "tags": ["method", "def", "function"],
      "content": "def method_name(parameters)\n  # method body\nend"
    },
    {
      "id": "class_def",
      "name": "Class Definition",
      "description": "Define a class with initialize",
      "category": "classes",
      "tags": ["class", "initialize", "oop"],
      "content": "class ClassName\n  def initialize(parameters)\n    # constructor\n  end\nend"
    },
    {
      "id": "begin_rescue",
      "name": "Begin/Rescue Block",
      "description": "Handle exceptions",
      "category": "error_handling",
      "tags": ["begin", "rescue", "exception", "error"],
      "content": "begin\n  # code that might raise\nrescue ExceptionType => e\n  # handle exception\nend"
    },
    {
      "id": "block_do",
      "name": "Block (do/end)",
      "description": "Multi-line block",
      "category": "blocks",
      "tags": ["block", "do", "end"],
      "content": "method_name do |param|\n  # block body\nend"
    }
  ]
}
```

### 6.3 General Text Library

```json
{
  "name": "Common Text Templates",
  "description": "General-purpose text snippets for documents and communication",
  "language": "text",
  "version": "1.0",
  "author": "Fragillidae Software",
  "snippets": [
    {
      "id": "letter_formal",
      "name": "Formal Business Letter",
      "description": "Standard formal letter structure",
      "category": "letters",
      "tags": ["letter", "formal", "business"],
      "content": "[Your Name]\n[Your Address]\n[City, State ZIP]\n[Your Email]\n[Date]\n\n[Recipient Name]\n[Title]\n[Company Name]\n[Address]\n[City, State ZIP]\n\nDear [Recipient Name]:\n\n[Opening paragraph - state purpose of letter]\n\n[Body paragraphs - provide details and supporting information]\n\n[Closing paragraph - summarize and state desired action]\n\nSincerely,\n\n\n[Your Signature]\n[Your Typed Name]\n[Your Title]"
    },
    {
      "id": "email_followup",
      "name": "Follow-up Email",
      "description": "Professional follow-up message",
      "category": "email",
      "tags": ["email", "followup", "professional"],
      "content": "Subject: Following Up - [Topic]\n\nHi [Name],\n\nI wanted to follow up on [topic/previous conversation].\n\n[Brief context or reminder]\n\n[Request or question]\n\nPlease let me know if you have any questions.\n\nBest,\n[Your Name]"
    },
    {
      "id": "meeting_notes",
      "name": "Meeting Notes Template",
      "description": "Structure for capturing meeting information",
      "category": "meetings",
      "tags": ["meeting", "notes", "minutes"],
      "content": "Meeting Notes\n=============\n\nDate: [Date]\nTime: [Start Time] - [End Time]\nAttendees: [Names]\n\nAgenda\n------\n1. [Topic 1]\n2. [Topic 2]\n3. [Topic 3]\n\nDiscussion\n----------\n[Key points discussed]\n\nDecisions\n---------\n[Decisions made]\n\nAction Items\n------------\n[ ] [Task] - [Owner] - [Due Date]\n[ ] [Task] - [Owner] - [Due Date]\n\nNext Meeting\n------------\nDate: [Next Date]\nTopics: [Planned topics]"
    }
  ]
}
```

### 6.4 JavaScript Code Library

```json
{
  "name": "JavaScript Snippets",
  "description": "Common JavaScript code structures",
  "language": "javascript",
  "file_extensions": [".js", ".mjs", ".jsx"],
  "version": "1.0",
  "author": "Fragillidae Software",
  "snippets": [
    {
      "id": "for_loop",
      "name": "For Loop",
      "description": "Classic for loop",
      "category": "loops",
      "tags": ["for", "loop", "iteration"],
      "content": "for (let i = 0; i < count; i++) {\n    // loop body\n}"
    },
    {
      "id": "for_of",
      "name": "For...Of Loop",
      "description": "Iterate over iterable values",
      "category": "loops",
      "tags": ["for", "of", "loop", "iteration"],
      "content": "for (const item of collection) {\n    // process item\n}"
    },
    {
      "id": "arrow_function",
      "name": "Arrow Function",
      "description": "Arrow function expression",
      "category": "functions",
      "tags": ["arrow", "function", "lambda"],
      "content": "const functionName = (parameters) => {\n    // function body\n};"
    },
    {
      "id": "async_function",
      "name": "Async Function",
      "description": "Asynchronous function declaration",
      "category": "async",
      "tags": ["async", "await", "function"],
      "content": "async function functionName(parameters) {\n    // async function body\n}"
    },
    {
      "id": "try_catch",
      "name": "Try/Catch Block",
      "description": "Exception handling",
      "category": "error_handling",
      "tags": ["try", "catch", "error", "exception"],
      "content": "try {\n    // code that might throw\n} catch (error) {\n    // handle error\n}"
    },
    {
      "id": "class_def",
      "name": "Class Definition",
      "description": "ES6 class with constructor",
      "category": "classes",
      "tags": ["class", "constructor", "oop"],
      "content": "class ClassName {\n    constructor(parameters) {\n        // initialize\n    }\n    \n    methodName() {\n        // method body\n    }\n}"
    }
  ]
}
```

---

## 7. Validation

### 7.1 Validation Rules

Applications loading snippet libraries should validate:

1. **Required fields** exist (`name`, `snippets`, `id`, `name`, `content`)
2. **ID uniqueness** within each library
3. **ID format** matches pattern `^[a-z][a-z0-9_]*$`
4. **Content is non-empty** for all snippets
5. **JSON syntax** is valid

### 7.2 Error Handling

Recommended behavior for invalid libraries:

- Log detailed error with file path and specific issue
- Skip the invalid library (don't crash the application)
- Continue loading other valid libraries
- Optionally notify user of load failures

---

## 8. Language Identifiers

Recommended `language` values for consistency:

| Language | Identifier |
|----------|------------|
| Plain text | `text` |
| Python | `python` |
| Ruby | `ruby` |
| JavaScript | `javascript` |
| TypeScript | `typescript` |
| HTML | `html` |
| CSS | `css` |
| Racket | `racket` |
| Scheme | `scheme` |
| SQL | `sql` |
| Bash/Shell | `bash` |
| C | `c` |
| C++ | `cpp` |
| Java | `java` |
| Go | `go` |
| Rust | `rust` |
