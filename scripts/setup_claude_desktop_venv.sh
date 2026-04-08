#!/usr/bin/env bash
# Create a venv and install pdf-porter into it. Claude Desktop (or the MCP host)
# runs this venv's Python so Docling and its weights live in one place.
# - macOS: defaults to ~/Library/Application Support/Claude/venv
# - Linux (e.g. VM with /mnt): defaults to /mnt/claude_venv so Docling stays on the VM.
# Override with CLAUDE_VENV.
set -euo pipefail

case "$(uname -s)" in
  Darwin)
    CLAUDE_VENV="${CLAUDE_VENV:-$HOME/Library/Application Support/Claude/venv}"
    ;;
  *)
    # VM / Linux: keep venv and Docling under /mnt so everything stays there.
    CLAUDE_VENV="${CLAUDE_VENV:-/mnt/claude_venv}"
    ;;
esac

echo "Using venv: $CLAUDE_VENV"
mkdir -p "$(dirname "$CLAUDE_VENV")"
uv venv "$CLAUDE_VENV"
uv pip install --python "$CLAUDE_VENV/bin/python" pdf-porter

echo ""
echo "Done. Add the snippet below to your MCP config (e.g. claude_desktop_config.json):"
echo ""
printf '%s\n' "{"
printf '  %s\n' '"mcpServers": {'
printf '    %s\n' '"pdf-tools": {'
printf '      %s\n' '"command": "'"$CLAUDE_VENV/bin/python"'",'
printf '      %s\n' '"args": ["-m", "pdf_porter.server"]'
printf '    %s\n' '}'
printf '  %s\n' '}'
printf '%s\n' "}"
echo ""
echo "Then restart Claude Desktop."
