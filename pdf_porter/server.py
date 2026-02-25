import base64 as _base64
import sys
import tempfile
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
def pdf_to_markdown(
    path: str | None = None,
    pdf_base64: str | None = None,
    save_output: bool = False,
    output_dir: str | None = None,
    filename: str | None = None,
) -> str:
    """Convert a PDF to Markdown using Docling's layout-aware converter.

    Args:
        path: Absolute or relative path to a local PDF file. Use this when the
              file genuinely exists on the server's filesystem.
        pdf_base64: Base64-encoded PDF bytes. Use this when the PDF arrives as
                    an attachment (e.g. claude.ai uploads where
                    /mnt/user-data/uploads/ is not accessible to the server).
        save_output: If True, write Markdown to a .md file and return the bare
                     file path. If False (default), return Markdown content directly.
        output_dir: Directory to write output when save_output=True. Defaults to
                    the same directory as the source file (path mode) or a temp
                    directory (base64 mode). Pass /mnt/user-data/outputs/ to
                    surface the file via Claude Desktop's present_files tool.
        filename: Original filename hint used when save_output=True in base64 mode.
                  E.g. pass "quarterly_report.pdf" so the output is
                  "quarterly_report.md" rather than "output.md". Ignored in path mode.

    Returns:
        Markdown string, the bare output file path if save_output=True, or
        "Error: ..." on failure.
    """
    tmp_path = None
    try:
        if pdf_base64 is not None:
            pdf_bytes = _base64.b64decode(pdf_base64)
            tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
            tmp.write(pdf_bytes)
            tmp.close()
            tmp_path = Path(tmp.name)
            source = tmp_path
            stem = Path(filename).stem if filename else "output"
        elif path is not None:
            source = Path(path)
            if not source.exists():
                if "/mnt/user-data/uploads/" in path or path.startswith("/mnt/user-data/uploads"):
                    return (
                        f"Error: file not found: {path}. "
                        "Paths under /mnt/user-data/uploads/ are not visible to this server. "
                        "Pass the PDF content as the pdf_base64 argument instead (e.g. after reading the file on the client)."
                    )
                return f"Error: file not found: {path}"
            if source.suffix.lower() != ".pdf":
                return f"Error: not a PDF file: {path}"
            stem = source.stem
        else:
            return "Error: provide either path or pdf_base64"

        converter = _get_converter()
        result = converter.convert(str(source))
        markdown = result.document.export_to_markdown()

        if save_output:
            if output_dir is not None:
                out_dir = Path(output_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
            else:
                out_dir = source.parent
            output_path = out_dir / (stem + ".md")
            output_path.write_text(markdown, encoding="utf-8")
            return str(output_path)

        return markdown

    except Exception as e:
        return f"Error: {e}"
    finally:
        # Clean up temp PDF created for base64 mode
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def main() -> None:
    # Pre-load Docling models at startup so the first tool call isn't slow.
    _get_converter()
    mcp.run()


if __name__ == "__main__":
    main()
