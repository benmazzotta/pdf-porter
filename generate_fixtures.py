"""Generate test fixture PDFs using reportlab. Run once to populate tests/fixtures/."""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus.doctemplate import BaseDocTemplate

FIXTURES = Path(__file__).parent / "tests" / "fixtures"
FIXTURES.mkdir(parents=True, exist_ok=True)

LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute "
    "irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla "
    "pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia "
    "deserunt mollit anim id est laborum."
)

styles = getSampleStyleSheet()


def make_simple():
    path = FIXTURES / "simple.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    h1 = ParagraphStyle("h1", parent=styles["Heading1"])
    body = styles["BodyText"]
    story = [
        Paragraph("Introduction to PDF Porter", h1),
        Spacer(1, 0.2 * inch),
        Paragraph(LOREM, body),
        Spacer(1, 0.2 * inch),
        Paragraph(LOREM, body),
        Spacer(1, 0.2 * inch),
        Paragraph(LOREM, body),
    ]
    doc.build(story)
    print(f"  wrote {path}")


def make_two_column():
    path = FIXTURES / "two_column.pdf"

    col_a_text = (
        "Column A: This text appears in the left column. "
        "It discusses the first topic at length. " + LOREM
    )
    col_b_text = (
        "Column B: This text appears in the right column. "
        "It discusses the second topic at length. " + LOREM
    )

    class TwoColDoc(BaseDocTemplate):
        def build(self, flowables, **kwargs):
            self._calc()
            w, h = self.pagesize
            margin = 0.75 * inch
            col_w = (w - 2 * margin - 0.25 * inch) / 2
            col_h = h - 2 * margin
            frame_a = Frame(margin, margin, col_w, col_h, id="col_a")
            frame_b = Frame(margin + col_w + 0.25 * inch, margin, col_w, col_h, id="col_b")
            template = PageTemplate(id="two_col", frames=[frame_a, frame_b])
            self.addPageTemplates([template])
            super().build(flowables, **kwargs)

    doc = TwoColDoc(str(path), pagesize=letter)
    body = styles["BodyText"]
    story = [
        Paragraph(col_a_text, body),
        Paragraph(col_b_text, body),
    ]
    doc.build(story)
    print(f"  wrote {path}")


def make_table():
    path = FIXTURES / "table.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter)
    data = [
        ["Name", "Value", "Notes"],
        ["Alpha",   "1.00",  "First entry in the dataset"],
        ["Beta",    "2.50",  "Secondary measurement"],
        ["Gamma",   "3.75",  "Tertiary value, reviewed"],
        ["Delta",   "4.20",  "Final row, pending audit"],
    ]
    table = Table(data, colWidths=[2 * inch, 1.5 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID",       (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
    ]))
    story = [
        Paragraph("Sample Data Table", styles["Heading1"]),
        Spacer(1, 0.2 * inch),
        table,
    ]
    doc.build(story)
    print(f"  wrote {path}")


if __name__ == "__main__":
    print("Generating fixture PDFs...")
    make_simple()
    make_two_column()
    make_table()
    print("Done.")
