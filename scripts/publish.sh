#!/usr/bin/env bash
# Build and publish pdf-porter to PyPI.
#
# Token source (first match wins):
#   1. PYPI_TOKEN environment variable
#   2. A file path given as the first argument:  scripts/publish.sh /path/to/token-file
#   3. PYPI_TOKEN_FILE environment variable (a file path)
# The token file must contain only the token (pypi-...). It is never echoed.
set -euo pipefail

cd "$(dirname "$0")/.."

token="${PYPI_TOKEN:-}"
token_file="${1:-${PYPI_TOKEN_FILE:-}}"

if [[ -z "$token" && -n "$token_file" ]]; then
  if [[ ! -r "$token_file" ]]; then
    echo "Error: token file not readable: $token_file" >&2
    exit 1
  fi
  token="$(< "$token_file")"
fi

if [[ -z "$token" ]]; then
  echo "Error: no PyPI token. Pass a token file path, or set PYPI_TOKEN or PYPI_TOKEN_FILE." >&2
  exit 1
fi

version="$(grep -m1 '^version = ' pyproject.toml | cut -d'"' -f2)"
echo "Publishing pdf-porter ${version}"

uv build
# Upload only this version's artifacts, never stale builds left in dist/.
UV_PUBLISH_TOKEN="$token" uv publish dist/pdf_porter-"${version}"*
