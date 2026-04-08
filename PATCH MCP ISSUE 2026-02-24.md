PATCH MCP ISSUE 2026-02-24

# pdf-porter Claude Desktop Extension — Patch Spec

## Concept

This is a patch, not a rebuild. The extension structure is correct. The single failure point is that Claude Desktop launches the MCP server in a clean subprocess with no inherited Python environment. The `docling` library (and its dependencies) aren't visible at runtime because they were never vendored into the extension bundle.

The fix has two parts: vendor all PyPI dependencies into a `lib/` directory inside the extension, and set `PYTHONPATH` in the manifest so the server process can find them.

---

## Current State (What's Broken)

Claude Desktop unpacks the `.mcpb` archive and spawns the server process. That process has no access to the developer's local `site-packages`. Any `import docling` call fails with `ModuleNotFoundError` — silently from the user's perspective.

Works in isolation because the developer's shell inherits their virtualenv or global Python environment. Claude Desktop does not.

---

## Implementation

### Step 1 — Vendor dependencies

From the extension root directory:

```bash
pip install docling --target ./lib
```

This installs `docling` and its full dependency tree into `./lib`. The directory travels inside the `.mcpb` ZIP at pack time.

> Note: Docling's dependency tree is large (~200MB uncompressed). Acceptable for local use; worth noting before submitting to the extension directory.

### Step 2 — Update manifest.json

Add `PYTHONPATH` to the server's env block. The `${__dirname}` template literal is replaced by Claude Desktop with the extension's unpacked directory at runtime.

```json
{
  "mcpb_version": "0.1",
  "name": "pdf-porter",
  "version": "1.0.0",
  "description": "Convert PDFs to Markdown using Docling",
  "author": {
    "name": "Your Name"
  },
  "server": {
    "type": "python",
    "entry_point": "server/main.py",
    "mcp_config": {
      "command": "python",
      "args": ["${__dirname}/server/main.py"],
      "env": {
        "PYTHONPATH": "${__dirname}/lib"
      }
    }
  }
}
```

If your manifest already has an `env` block, add `PYTHONPATH` to it. Don't replace existing entries.

### Step 3 — Repack

```bash
npx @anthropic-ai/mcpb pack
```

Validate that `lib/` appears in the generated archive:

```bash
unzip -l pdf-porter.mcpb | grep "^.*lib/" | head -5
```

If no `lib/` entries appear, the vendor step didn't run from the right directory. Recheck your working directory and repeat Step 1.

### Final directory structure

```
extension/
├── manifest.json
├── server/
│   └── main.py
├── lib/                  # vendored — added by this patch
│   ├── docling/
│   └── [docling dependencies]/
└── icon.png
```

---

## Specs

| Requirement | Detail |
|---|---|
| `lib/` present in archive | All docling deps vendored via `pip install --target` |
| `PYTHONPATH` set in manifest | Points to `${__dirname}/lib` |
| No global Python dependency | Extension must work on a machine where docling is not installed |
| No virtualenv required | User should not need to activate anything |
| Works on macOS and Windows | `${__dirname}` resolves correctly on both platforms via Claude Desktop |

---

## Testing

### Unit — import resolves

Before packing, confirm the vendored path works in isolation:

```bash
PYTHONPATH=./lib python -c "import docling; print('ok')"
```

Expected: `ok`. If this fails, the vendor step is incomplete.

### Integration — server starts clean

Launch the server the same way Claude Desktop will, with no inherited environment:

```bash
env -i PYTHONPATH=/absolute/path/to/lib python server/main.py
```

Expected: server starts and waits for MCP input without import errors.

### End-to-end — install in Claude Desktop

1. Drag the `.mcpb` file into Claude Desktop Settings > Extensions.
2. Click Install.
3. Open a new conversation and call the `pdf_to_markdown` tool with a test PDF.
4. Confirm markdown is returned.

### Regression — clean machine

Test on a machine (or a fresh Docker container) where `docling` is **not** globally installed. The extension must work identically. This is the definitive test — if it passes here, the patch is complete.

```dockerfile
FROM python:3.11-slim
# Do NOT install docling here
COPY extension/ /extension/
RUN cd /extension && env -i PYTHONPATH=/extension/lib python server/main.py &
# Run your MCP smoke test
```

### Negative — missing lib/

Repack *without* running the vendor step and confirm the tool fails with a clear `ModuleNotFoundError`. This documents the failure mode for future contributors.