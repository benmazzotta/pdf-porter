"""Integration tests for pdf_to_markdown. Does NOT mock DocumentConverter."""
import base64
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
    assert Path(result) == dest.with_suffix(".md")
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0


def test_base64_mode():
    pdf_bytes = (FIXTURES / "simple.pdf").read_bytes()
    b64 = base64.b64encode(pdf_bytes).decode()
    result = pdf_to_markdown(pdf_base64=b64)
    assert isinstance(result, str)
    assert len(result) > 100
    assert not result.startswith("Error:")


def test_base64_save_output(tmp_path):
    pdf_bytes = (FIXTURES / "simple.pdf").read_bytes()
    b64 = base64.b64encode(pdf_bytes).decode()
    result = pdf_to_markdown(pdf_base64=b64, save_output=True, output_dir=str(tmp_path))
    assert Path(result).exists()
    assert Path(result).suffix == ".md"
    assert Path(result).stat().st_size > 0


def test_output_dir(tmp_path):
    result = pdf_to_markdown(
        str(FIXTURES / "simple.pdf"), save_output=True, output_dir=str(tmp_path)
    )
    assert Path(result) == tmp_path / "simple.md"
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0


def test_neither_arg_returns_error():
    result = pdf_to_markdown()
    assert result.startswith("Error:")


def test_base64_filename_hint(tmp_path):
    pdf_bytes = (FIXTURES / "simple.pdf").read_bytes()
    b64 = base64.b64encode(pdf_bytes).decode()
    result = pdf_to_markdown(
        pdf_base64=b64,
        save_output=True,
        output_dir=str(tmp_path),
        filename="quarterly_report.pdf",
    )
    assert Path(result).name == "quarterly_report.md"
    assert Path(result).stat().st_size > 0


def test_unwritable_output_dir_returns_error():
    result = pdf_to_markdown(
        str(FIXTURES / "simple.pdf"),
        save_output=True,
        output_dir="/proc/pdf_porter_test",
    )
    assert result.startswith("Error:")
