# CLAUDE.md

## Project
MCP server exposing PDF→Markdown conversion via Docling. Single tool: `pdf_to_markdown(path)`.

## Stack
- Python 3.11+
- `mcp[cli]` (FastMCP)
- `docling`
- `uv` for packaging and running

## Structure
```
mcp_docling/
  __init__.py
  server.py       # FastMCP app, tool definitions
tests/
  test_server.py
  fixtures/       # sample PDFs: simple, two-column, table-heavy, scanned
pyproject.toml
README.md
CLAUDE.md
```

## Commands
```bash
uv run python -m mcp_docling          # start server
uv run pytest                         # run tests
uv run mcp dev mcp_docling/server.py  # MCP inspector
```

## Rules
- No global state. Converter instantiated per-call or cached as module-level singleton — your call, but document it.
- All errors surface as readable strings, never raw tracebacks to the LLM.
- Tests must include at least one multi-column PDF and one table PDF.
- Do not add dependencies beyond mcp, docling, and pytest.
- README must include working claude_desktop_config.json snippet before tests pass.
