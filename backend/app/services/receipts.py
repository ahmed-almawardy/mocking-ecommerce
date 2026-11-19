from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


RECEIPT_DIR = Path("/app/receipts")


def generate_receipt(order) -> str:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    target = RECEIPT_DIR / f"{order.order_number}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(target), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm)
    story = [Paragraph("NOVA HOME", styles["Title"]), Paragraph("Order receipt", styles["Heading2"]), Spacer(1, 8*mm)]
    story += [Paragraph(f"Order: {order.order_number}", styles["Normal"]),
              Paragraph(f"Customer: {order.shipping_name}", styles["Normal"]),
              Paragraph(f"Delivery: {order.shipping_address}, {order.shipping_city}", styles["Normal"]), Spacer(1, 8*mm)]
    rows = [["Product", "SKU", "Qty", "Unit price", "Line total"]]
    for item in order.items:
        rows.append([item.product_name, item.sku, str(item.quantity), f"EGP {item.unit_price:.2f}", f"EGP {item.line_total:.2f}"])
    rows += [["", "", "", "Subtotal", f"EGP {order.subtotal:.2f}"], ["", "", "", "Shipping", f"EGP {order.shipping_fee:.2f}"], ["", "", "", "Total paid", f"EGP {order.total:.2f}"]]
    table = Table(rows, colWidths=[70*mm, 32*mm, 15*mm, 30*mm, 30*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#ed1c24")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dddddd")),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("Thank you for shopping with NOVA HOME.", styles["Normal"]))
    doc.build(story)
    return str(target)
