from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as RLImage, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import barcode
from barcode.writer import ImageWriter

def _get_barcode_bytes(sku: str) -> BytesIO:
    code128 = barcode.get_barcode_class('code128')
    rv = BytesIO()
    bc = code128(sku, writer=ImageWriter())
    bc.write(rv, options={'module_width': 0.18, 'module_height': 7.0, 'font_size': 6, 'quiet_zone': 1.0})
    rv.seek(0)
    return rv

def generate_pdf_thermal(products: list[dict], width_mm: float = 50.0, height_mm: float = 30.0) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(width_mm * mm, height_mm * mm), leftMargin=2*mm, rightMargin=2*mm, topMargin=2*mm, bottomMargin=2*mm)
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle('T', fontName='Helvetica-Bold', fontSize=7, leading=8, alignment=1)
    style_sub = ParagraphStyle('S', fontName='Helvetica', fontSize=7, leading=8, alignment=1)
    
    story = []
    for idx, prod in enumerate(products):
        story.append(Paragraph(f"<b>{prod['name'][:22]}</b>", style_title))
        story.append(Spacer(1, 1*mm))
        bc_img = RLImage(_get_barcode_bytes(prod['sku']), width=44*mm, height=12*mm)
        story.append(bc_img)
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(f"SKU: {prod['sku']} | <b>€{prod['unit_price']:.2f}</b>", style_sub))
        if idx < len(products) - 1:
            story.append(PageBreak())

    doc.build(story)
    buffer.seek(0)
    return buffer