from __future__ import annotations

from io import BytesIO
from textwrap import wrap


def build_pdf_report(title: str, lines: list[str]) -> bytes | None:
    """Return a compact PDF report, or None when reportlab is unavailable."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfgen import canvas
    except ImportError:
        return None

    buffer = BytesIO()
    page = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x = 2 * cm
    y = height - 2 * cm

    page.setTitle(title)
    page.setFont("Helvetica-Bold", 16)
    page.drawString(x, y, title)
    y -= 1.0 * cm

    page.setFont("Helvetica", 10)
    for line in lines:
        for chunk in wrap(line, width=92):
            if y < 2 * cm:
                page.showPage()
                page.setFont("Helvetica", 10)
                y = height - 2 * cm
            page.drawString(x, y, chunk)
            y -= 0.48 * cm
        y -= 0.15 * cm

    page.save()
    buffer.seek(0)
    return buffer.getvalue()
