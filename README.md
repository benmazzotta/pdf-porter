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
| `path` | `str` | — | Path to a PDF on the **server’s** filesystem |
| `pdf_base64` | `str` | — | Base64-encoded PDF bytes (use for uploads; see below) |
| `save_output` | `bool` | `False` | If `True`, writes a `.md` file and returns the output path |
| `output_dir` | `str` | — | Directory for the `.md` file when `save_output=True` (e.g. `/mnt/user-data/outputs/`) |
| `filename` | `str` | — | Original filename hint for base64 mode (e.g. `"report.pdf"` → output is `"report.md"`) |

You must pass either `path` or `pdf_base64` (not both). Paths under `/mnt/user-data/uploads/` (e.g. Claude Desktop uploads) are not visible to the server; for those, pass the file content as `pdf_base64` instead.

**Returns:** Markdown string, or a bare output file path when `save_output=True`, or `"Error: <message>"` on failure.

## Known Limitations

- **First run:** Docling downloads model weights (~500MB). You'll see a pause. Subsequent runs are fast.
- **Scanned PDFs:** OCR mode is not enabled in v0.1. Image-only PDFs will return empty or minimal text.
- **Windows:** Path handling not validated on Windows.

## License

MIT. See [LICENSE](LICENSE).
