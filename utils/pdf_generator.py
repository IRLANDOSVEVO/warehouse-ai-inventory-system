"""PDF thermal label generator with barcode support."""
from io import BytesIO

import barcode
from barcode.writer import ImageWriter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage, PageBreak, Paragraph, SimpleDocTemplate, Spacer


def _get_barcode_bytes(sku: str) -> BytesIO:
    """Generate Code128 barcode image bytes.

    Args:
        sku: Product SKU to encode

    Returns:
        BytesIO: Barcode image buffer in PNG format
    """
    code128 = barcode.get_barcode_class("code128")
    buffer = BytesIO()
    bc = code128(sku, writer=ImageWriter())
    bc.write(
        buffer,
        options={
            "module_width": 0.18,
            "module_height": 7.0,
            "font_size": 6,
            "quiet_zone": 1.0,
        },
    )
    buffer.seek(0)
    return buffer


def generate_pdf_thermal(
    products: list[dict], width_mm: float = 50.0, height_mm: float = 30.0
) -> BytesIO:
    """Generate thermal label PDF with barcodes.

    Args:
        products: List of product dictionaries with keys:
            - name: Product name
            - sku: Product SKU
            - unit_price: Unit price in EUR
        width_mm: Label width in millimeters (default: 50mm)
        height_mm: Label height in millimeters (default: 30mm)

    Returns:
        BytesIO: PDF buffer ready to download
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(width_mm * mm, height_mm * mm),
        leftMargin=2 * mm,
        rightMargin=2 * mm,
        topMargin=2 * mm,
        bottomMargin=2 * mm,
    )

    # Define text styles
    style_title = ParagraphStyle(
        "T", fontName="Helvetica-Bold", fontSize=7, leading=8, alignment=1
    )
    style_sub = ParagraphStyle("S", fontName="Helvetica", fontSize=7, leading=8, alignment=1)

    story = []
    for idx, prod in enumerate(products):
        # Extract product data with defaults
        name = str(prod.get("name", "") or "Prodotto")
        sku = str(prod.get("sku", "") or "N/A")
        unit_price = float(prod.get("unit_price", 0) or 0)

        # Build label content
        story.append(Paragraph(f"<b>{name[:22]}</b>", style_title))
        story.append(Spacer(1, 1 * mm))
        story.append(RLImage(_get_barcode_bytes(sku), width=44 * mm, height=12 * mm))
        story.append(Spacer(1, 1 * mm))
        story.append(Paragraph(f"SKU: {sku} | <b>€{unit_price:.2f}</b>", style_sub))

        # Add page break between labels (except last one)
        if idx < len(products) - 1:
            story.append(PageBreak())

    # Build PDF document
    doc.build(story)
    buffer.seek(0)
    return buffer
