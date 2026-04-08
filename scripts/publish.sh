#!/usr/bin/env bash
# Build and publish pdf-porter to PyPI. Requires PYPI_TOKEN in the environment.
set -euo pipefail

if [[ -z "${PYPI_TOKEN:-}" ]]; then
  echo "Error: PYPI_TOKEN is not set. Export it in your shell before running this script." >&2
  exit 1
fi

uv build
uv publish --token "$PYPI_TOKEN"
