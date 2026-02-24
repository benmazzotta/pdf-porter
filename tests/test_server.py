"""Integration tests for pdf_to_markdown. Does NOT mock DocumentConverter."""
import shutil
from pathlib import Path

import pytest

from pdf_porter.server import pdf_to_markdown

FIXTURES = Path(__file__).parent / "fixtures"


def test_simple_pdf():
    result = pdf_to_markdown(str(FIXTURES / "simple.pdf"))
    assert isinstance(result, str)
    assert len(result) > 100
    assert not result.startswith("Error:")


def test_two_column_pdf():
    result = pdf_to_markdown(str(FIXTURES / "two_column.pdf"))
    assert isinstance(result, str)
    assert len(result) > 100
    assert not result.startswith("Error:")


def test_table_pdf():
    result = pdf_to_markdown(str(FIXTURES / "table.pdf"))
    assert isinstance(result, str)
    assert "|" in result


def test_bad_path():
    result = pdf_to_markdown("/nonexistent/path/to/file.pdf")
    assert result.startswith("Error:")


def test_non_pdf(tmp_path):
    txt = tmp_path / "document.txt"
    txt.write_text("not a pdf")
    result = pdf_to_markdown(str(txt))
    assert result.startswith("Error:")


def test_save_output(tmp_path):
    src = FIXTURES / "simple.pdf"
    dest = tmp_path / "simple.pdf"
    shutil.copy(src, dest)
    result = pdf_to_markdown(str(dest), save_output=True)
    assert result.startswith("Saved to:")
    md_file = dest.with_suffix(".md")
    assert md_file.exists()
    assert md_file.stat().st_size > 0
