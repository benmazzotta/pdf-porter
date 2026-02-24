# mcp-docling: Concept Note & Implementation Plan

## Problem

Claude's native PDF ingestion is shallow. It reads text streams, not document structure. Tables become noise. Two-column papers read in the wrong order. Scanned PDFs return nothing. The result is that users paste PDFs into Claude and get confused or degraded responses — not because Claude is weak, but because the input is scrambled before Claude ever sees it.

## Solution

A local MCP server that wraps Docling — a layout-aware document converter — and exposes a single tool to Claude Desktop: `pdf_to_markdown(path)`. Claude calls it, gets clean structured markdown back, and reasons over that instead.

No upload. No cloud dependency. No background service. The server process lives only during a Claude Desktop session.

## Scope

**In:** PDF to markdown. Local file paths. Optional output-to-file.  
**Out:** Other document formats, cloud storage integration, batch processing, GUI. These are v2 concerns.

---

## Phase 1: Build

### Goal
A working MCP server that converts a local PDF to markdown and returns it to Claude.

### Prompt for Claude Code
```
Create a Python MCP server using FastMCP (mcp[cli] package) in mcp_docling/server.py.

Expose one tool: pdf_to_markdown(path: str, save_output: bool = False) -> str

Behavior:
- Validate that path exists and is a .pdf file. Return a clear error string if not.
- Use DocumentConverter from docling to convert the PDF.
- Call result.document.export_to_markdown().
- If save_output is True, write the markdown to the same directory as the PDF, 
  with the same filename and .md extension. Return the output path as a string.
- If save_output is False, return the markdown content directly.
- Catch all exceptions and return them as readable error strings prefixed with "Error: ".
- Cache the DocumentConverter as a module-level singleton to avoid reloading weights on every call.

Set up pyproject.toml with:
- name: mcp-docling
- version: 0.1.0
- dependencies: mcp[cli], docling
- dev dependencies: pytest
- entry point: mcp_docling.server:mcp (as mcp script)
- Python >= 3.11

Do not add any other dependencies.
```

### Acceptance Criteria
- [ ] `uv run python -m mcp_docling` starts without error
- [ ] `uv run mcp dev mcp_docling/server.py` opens MCP inspector
- [ ] Tool appears in inspector with correct signature
- [ ] Calling with a valid PDF path returns non-empty markdown string
- [ ] Calling with a bad path returns a readable error string, not a traceback
- [ ] `save_output=True` writes a `.md` file next to the PDF

---

## Phase 2: Test

### Goal
Confidence across the real-world PDF types that matter. This is where pypdf fails and docling earns its keep.

### Prompt for Claude Code
```
Create tests/test_server.py using pytest.

Download or generate four fixture PDFs into tests/fixtures/:
1. simple.pdf — single column, clean text (generate with reportlab if needed)
2. two_column.pdf — two-column layout (generate with reportlab)
3. table.pdf — PDF containing a markdown-renderable table (generate with reportlab)
4. scanned.pdf — use any freely licensed scanned PDF sample from a public URL, 
   or skip if download is unreliable and note it

For each fixture, write a test that:
- Calls pdf_to_markdown(path) directly (import the function, don't go through MCP)
- Asserts the result is a non-empty string
- Asserts no "Error:" prefix in result

Additional tests:
- Bad path returns string starting with "Error:"
- Non-PDF extension returns string starting with "Error:"
- save_output=True creates the expected .md file (use tmp_path fixture, copy a fixture there first)

Do not mock DocumentConverter. These are integration tests. They should call docling for real.
```

### Acceptance Criteria
- [ ] `uv run pytest` passes all tests
- [ ] Two-column test returns markdown where paragraphs are not interleaved
- [ ] Table test returns output containing a markdown table (`|` characters)
- [ ] Error path tests pass
- [ ] save_output test confirms file exists and is non-empty

---

## Phase 3: Package

### Goal
Anyone can run this with a single `uvx` command. No cloning required.

### Prompt for Claude Code
```
Prepare mcp-docling for PyPI publication.

1. Verify pyproject.toml is complete:
   - name, version, description, license (MIT), author, homepage, readme
   - Correct entry point so `uvx mcp-docling` starts the server

2. Write README.md with these sections:
   - One-sentence description
   - Installation (two methods: uvx one-liner, and uv add for development)
   - claude_desktop_config.json snippet showing exact configuration
   - Tool reference: pdf_to_markdown parameters and return values
   - Known limitations: large files, scanned PDFs need OCR mode, first-run weight download
   - License

3. Add LICENSE (MIT, author: Ben Mazzotta, year 2025)

4. Build the package:
   uv build

5. Confirm dist/ contains a .whl and .tar.gz

6. Dry-run install from the wheel locally to confirm the entry point works:
   uv run --with dist/mcp_docling-*.whl mcp-docling --help
   (adjust if FastMCP handles --help differently)
```

### Acceptance Criteria
- [ ] `uv build` completes without error
- [ ] `dist/` contains both wheel and sdist
- [ ] README contains working config snippet (verified by reading it)
- [ ] LICENSE file present
- [ ] Entry point is callable from the wheel

---

## Phase 4: Publish

### Goal
Package is live on PyPI. Users can configure it in two lines.

### Prompt for Claude Code
```
Publish mcp-docling to PyPI using uv.

Steps:
1. Ensure PYPI_TOKEN is available as environment variable (do not hardcode it)
2. Run: uv publish --token $PYPI_TOKEN
3. Wait ~60 seconds, then verify publication:
   curl https://pypi.org/pypi/mcp-docling/json | python -m json.tool | grep version
4. Test the live package:
   uvx mcp-docling
   (confirm it starts and prints MCP server startup message)
5. Update README if the PyPI badge URL or install command needs adjusting.

If PYPI_TOKEN is not set, stop and print instructions for the user to set it.
Do not attempt to publish without a token.
```

### Acceptance Criteria
- [ ] Package appears at pypi.org/project/mcp-docling
- [ ] `uvx mcp-docling` works in a clean environment (test in a new uv venv)
- [ ] Version on PyPI matches pyproject.toml
- [ ] README on PyPI renders correctly (check the PyPI project page)

---

## Risk Notes

**Docling weight download on first run.** Users will see a pause of 30–90 seconds the first time `pdf_to_markdown` is called. The README must warn them. Consider printing a log message from the server: `"Loading Docling models (first run only)..."`.

**Scanned PDFs.** Docling handles these but OCR mode must be enabled explicitly. v0.1 can document this as a known limitation and expose it as a future `ocr=True` parameter.

**Path handling on Windows.** Docling and MCP both support Windows but path separators can bite. Test on the platform you care about.

**PyPI name collision.** Check that `mcp-docling` is unclaimed before Phase 3. If taken, `mcp-pdf-docling` or `docling-mcp` are reasonable alternatives.
