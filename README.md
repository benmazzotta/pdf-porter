# pdf-porter

Layout-aware PDF to Markdown for Claude — one tool, zero config, five minutes to set up. Uses [Docling](https://github.com/DS4SD/docling) to preserve tables, multi-column layouts, and document structure that Claude's native PDF ingestion loses.

> If you want the full Docling toolset, see [docling-mcp](https://pypi.org/project/docling-mcp/) by IBM Research. pdf-porter is intentionally minimal: one tool, one job.

## Installation

### Use with Claude Desktop (recommended)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf-tools": {
      "command": "uvx",
      "args": ["pdf-porter"]
    }
  }
}
```

Then restart Claude Desktop. The first time Claude calls the tool, Docling will download its model weights (~500MB). Subsequent calls are fast.

### Development

```bash
git clone https://github.com/benmazzotta/pdf-porter
cd pdf-porter
uv sync --dev
uv run pytest
```

## Tool Reference

### `pdf_to_markdown`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `path` | `str` | required | Absolute or relative path to a PDF file |
| `save_output` | `bool` | `False` | If `True`, writes a `.md` file next to the PDF and returns the output path |

**Returns:** Markdown string, or `"Saved to: <path>"` when `save_output=True`, or `"Error: <message>"` on failure.

## Known Limitations

- **First run:** Docling downloads model weights (~500MB). You'll see a pause. Subsequent runs are fast.
- **Scanned PDFs:** OCR mode is not enabled in v0.1. Image-only PDFs will return empty or minimal text.
- **Windows:** Path handling not validated on Windows.

## License

MIT. See [LICENSE](LICENSE).
