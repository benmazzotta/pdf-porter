# Claude Code Prompt Sequence
## mcp-docling — Autonomous Build Session

Run these prompts in order in Claude Code. Each phase should complete fully before the next begins. If a phase fails its acceptance criteria, fix before proceeding.

---

## Prompt 0 — Bootstrap

```
Initialize a new Python project called mcp-docling.

Create this directory structure:
  mcp_docling/__init__.py
  mcp_docling/server.py
  tests/__init__.py
  tests/test_server.py
  tests/fixtures/   (empty for now)
  pyproject.toml
  README.md
  CLAUDE.md
  LICENSE

pyproject.toml requirements:
  - name: mcp-docling
  - version: 0.1.0
  - description: "MCP server for layout-aware PDF to Markdown conversion via Docling"
  - requires-python: ">=3.11"
  - dependencies: ["mcp[cli]", "docling"]
  - optional-dependencies.dev: ["pytest"]
  - [project.scripts] mcp-docling = "mcp_docling.server:main"
  - [project.urls] homepage = "https://github.com/benmazzotta/mcp-docling"

In mcp_docling/__init__.py, just set __version__ = "0.1.0".

Do not write server.py or tests yet. Confirm the scaffold is in place.
```

---

## Prompt 1 — Server

```
Write mcp_docling/server.py.

Use FastMCP from the mcp package. Create a module-level DocumentConverter singleton 
from docling.document_converter. Do not reinstantiate it on every call.

Expose one tool:

  pdf_to_markdown(path: str, save_output: bool = False) -> str

Behavior:
- If path does not exist: return "Error: file not found: {path}"
- If path does not end in .pdf (case-insensitive): return "Error: not a PDF file: {path}"
- Convert using DocumentConverter().convert(path), then export_to_markdown()
- If save_output is True: write markdown to same directory, same stem, .md extension.
  Return "Saved to: {output_path}"
- If save_output is False: return the markdown string directly
- Wrap everything in try/except Exception as e and return f"Error: {e}" on failure

Add a main() function:
  def main():
      mcp.run()

Add if __name__ == "__main__": main() at the bottom.

Log "Loading Docling models..." to stderr before the first conversion (not at import time — 
use a module-level flag).
```

---

## Prompt 2 — Fixtures and Tests

```
Generate test fixture PDFs in tests/fixtures/ using reportlab.
Add reportlab as a dev dependency if not present.

Generate three PDFs:

1. tests/fixtures/simple.pdf
   - Single column
   - Three paragraphs of Lorem Ipsum
   - One H1 heading

2. tests/fixtures/two_column.pdf
   - Two-column layout
   - Different text in each column, clearly labeled "Column A" and "Column B"

3. tests/fixtures/table.pdf
   - A table with 3 columns and 5 rows
   - Headers: Name, Value, Notes
   - Fill with sample data

Write a standalone script generate_fixtures.py at the project root that generates 
all three. Run it. Confirm all three files exist and are valid PDFs.

Then write tests/test_server.py:

Import pdf_to_markdown directly from mcp_docling.server (not through MCP).

Tests:
- test_simple_pdf: result is str, len > 100, no "Error:" prefix
- test_two_column_pdf: result is str, len > 100, no "Error:" prefix
- test_table_pdf: result contains "|" character
- test_bad_path: result starts with "Error:"
- test_non_pdf: create a temp .txt file, result starts with "Error:"
- test_save_output: copy simple.pdf to tmp_path, call with save_output=True,
  assert .md file exists and is non-empty

Run pytest. All tests must pass before proceeding.
```

---

## Prompt 3 — README and Packaging

```
Write README.md with these exact sections:

# mcp-docling

One sentence: what it does and why it's better than pypdf.

## Installation

### Use with Claude Desktop (recommended)
Add to claude_desktop_config.json:

{
  "mcpServers": {
    "pdf-tools": {
      "command": "uvx",
      "args": ["mcp-docling"]
    }
  }
}

Then restart Claude Desktop.

### Development
git clone https://github.com/benmazzotta/mcp-docling
cd mcp-docling
uv sync --dev
uv run pytest

## Tool Reference

### pdf_to_markdown
- path (str): absolute or relative path to a PDF file
- save_output (bool, default False): if True, writes .md file next to the PDF and returns the path

## Known Limitations
- First run downloads Docling model weights (~500MB). Subsequent runs are fast.
- Scanned PDFs: OCR mode is not enabled in v0.1. Text in image-only PDFs will be empty.
- Tested on macOS and Linux. Windows path handling not validated.

## License
MIT. See LICENSE.

---

Write LICENSE as MIT, author Ben Mazzotta, year 2025.

Then run:
  uv build

Confirm dist/ contains a .whl and a .tar.gz. Report the filenames.
```

---

## Prompt 4 — Publish

```
Publish to PyPI.

First, check whether PYPI_TOKEN is set in the environment.
If not set: print the following and stop:

  "To publish, set your PyPI API token:
   export PYPI_TOKEN=pypi-...
   Then re-run this prompt."

If set, run:
  uv publish --token $PYPI_TOKEN

After publishing, wait 60 seconds, then verify:
  curl -s https://pypi.org/pypi/mcp-docling/json | python -m json.tool | grep '"version"'

Then test the live package in a temporary directory:
  cd /tmp
  uvx mcp-docling &
  sleep 5
  kill %1

Confirm it starts without error. Report success or failure clearly.
```

---

## Final Checklist

After all four prompts complete, verify:

- [ ] `uv run pytest` — all tests green
- [ ] `uv build` — dist/ has wheel and sdist  
- [ ] `uvx mcp-docling` — server starts
- [ ] Package visible at pypi.org/project/mcp-docling
- [ ] README on PyPI renders correctly
- [ ] claude_desktop_config.json snippet in README is accurate
