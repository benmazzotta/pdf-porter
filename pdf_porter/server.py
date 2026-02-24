import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from docling.document_converter import DocumentConverter

mcp = FastMCP("pdf-porter")

# Module-level singleton — avoids reloading model weights on every call.
_converter: DocumentConverter | None = None
_first_run = True


def _get_converter() -> DocumentConverter:
    global _converter, _first_run
    if _converter is None:
        if _first_run:
            print("Loading Docling models (first run only)...", file=sys.stderr)
            _first_run = False
        _converter = DocumentConverter()
    return _converter


@mcp.tool()
def pdf_to_markdown(path: str, save_output: bool = False) -> str:
    """Convert a local PDF file to Markdown using Docling's layout-aware converter.

    Args:
        path: Absolute or relative path to a PDF file.
        save_output: If True, write the Markdown to a .md file next to the PDF
                     and return the output path. If False (default), return the
                     Markdown content directly.

    Returns:
        Markdown string, output path (if save_output=True), or "Error: ..." on failure.
    """
    try:
        p = Path(path)
        if not p.exists():
            return f"Error: file not found: {path}"
        if p.suffix.lower() != ".pdf":
            return f"Error: not a PDF file: {path}"

        converter = _get_converter()
        result = converter.convert(str(p))
        markdown = result.document.export_to_markdown()

        if save_output:
            output_path = p.with_suffix(".md")
            output_path.write_text(markdown, encoding="utf-8")
            return f"Saved to: {output_path}"

        return markdown

    except Exception as e:
        return f"Error: {e}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
