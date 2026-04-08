#!/usr/bin/env bash
# Run pdf-porter from this repo's venv. Use this as Claude Desktop command so
# Docling is installed once in the project; no dependency on uv global cache.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run pdf-porter
