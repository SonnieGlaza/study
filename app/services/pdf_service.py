from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.schemas import PersonalityResult


def render_personality_pdf(full_name: str, result: PersonalityResult) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Interior Personality Result",
    )

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        leading=16,
        spaceAfter=10,
    )

    story = [
        Paragraph("Персональная интерьерная карта", title_style),
        Spacer(1, 10),
        Paragraph(f"Пользователь: {full_name or 'Без имени'}", body_style),
        Paragraph(f"Тип личности: <b>{result.personality_type}</b>", body_style),
        Paragraph(result.personality_description, body_style),
        Paragraph("<b>Рекомендации по интерьеру:</b>", body_style),
        Paragraph(result.interior_recommendations, body_style),
    ]
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
