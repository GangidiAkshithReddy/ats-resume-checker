from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle", fontSize=20, leading=24, spaceAfter=4,
        textColor=colors.HexColor("#1f2937"), fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", fontSize=13, leading=16, spaceBefore=14,
        spaceAfter=6, textColor=colors.HexColor("#4f46e5"), fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="BodyTextCustom", fontSize=10, leading=14,
        textColor=colors.HexColor("#374151")
    ))
    styles.add(ParagraphStyle(
        name="ScoreBig", fontSize=28, leading=32, fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="SmallGray", fontSize=8, leading=11,
        textColor=colors.HexColor("#9ca3af")
    ))
    return styles


def score_color(score):
    if score >= 75:
        return colors.HexColor("#16a34a")
    elif score >= 50:
        return colors.HexColor("#d97706")
    else:
        return colors.HexColor("#dc2626")


def rating_label(rating):
    return {
        "strong": "Strong",
        "needs_work": "Needs Work",
        "missing": "Missing",
    }.get(rating, rating)


def build_pdf_report(match_result, formatting_issues, ai_sections=None, ai_rewrites=None):
    """Build a PDF report and return it as bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch, rightMargin=0.7 * inch,
    )
    styles = build_styles()
    story = []

    # Title
    story.append(Paragraph("ATS Resume Check Report", styles["ReportTitle"]))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e5e7eb"), thickness=1))
    story.append(Spacer(1, 12))

    # Score
    score = match_result["score"]
    score_style = ParagraphStyle(
        "ScoreColored", parent=styles["ScoreBig"], textColor=score_color(score)
    )
    story.append(Paragraph(f"Match Score: {score}%", score_style))
    story.append(Spacer(1, 10))

    # AI Summary
    if ai_sections and ai_sections.get("overall_summary"):
        story.append(Paragraph("Overall Summary", styles["SectionHeading"]))
        story.append(Paragraph(ai_sections["overall_summary"], styles["BodyTextCustom"]))
        story.append(Spacer(1, 6))

    # Section feedback
    if ai_sections and ai_sections.get("sections"):
        story.append(Paragraph("Section-by-Section Feedback", styles["SectionHeading"]))
        table_data = [["Section", "Rating", "Feedback"]]
        for sec in ai_sections["sections"]:
            table_data.append([
                Paragraph(sec.get("section_name", ""), styles["BodyTextCustom"]),
                Paragraph(rating_label(sec.get("rating", "")), styles["BodyTextCustom"]),
                Paragraph(sec.get("feedback", ""), styles["BodyTextCustom"]),
            ])

        tbl = Table(table_data, colWidths=[1.3 * inch, 0.9 * inch, 3.8 * inch])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 10))

    # Top priorities
    if ai_sections and ai_sections.get("top_priorities"):
        story.append(Paragraph("Top Priorities", styles["SectionHeading"]))
        for i, item in enumerate(ai_sections["top_priorities"], 1):
            story.append(Paragraph(f"{i}. {item}", styles["BodyTextCustom"]))
        story.append(Spacer(1, 10))

    # Keyword matches
    story.append(Paragraph("Keyword Match", styles["SectionHeading"]))
    matched = ", ".join(match_result.get("matched", [])) or "None found"
    missing = ", ".join(match_result.get("missing", [])) or "None"
    story.append(Paragraph(f"<b>Found in resume:</b> {matched}", styles["BodyTextCustom"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Missing from resume:</b> {missing}", styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))

    # Formatting issues
    story.append(Paragraph("Formatting & Parsing Checks", styles["SectionHeading"]))
    if formatting_issues:
        for issue in formatting_issues:
            story.append(Paragraph(f"- {issue}", styles["BodyTextCustom"]))
    else:
        story.append(Paragraph("No major formatting issues detected.", styles["BodyTextCustom"]))
    story.append(Spacer(1, 10))

    # Bullet rewrite suggestions
    if ai_rewrites and ai_rewrites.get("rewrites"):
        story.append(Paragraph("Suggested Bullet Rewrites", styles["SectionHeading"]))
        for r in ai_rewrites["rewrites"]:
            story.append(Paragraph(f"<b>Original:</b> {r.get('original', '')}", styles["BodyTextCustom"]))
            story.append(Paragraph(f"<b>Improved:</b> {r.get('improved', '')}", styles["BodyTextCustom"]))
            story.append(Paragraph(f"<i>{r.get('why', '')}</i>", styles["SmallGray"]))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#e5e7eb"), thickness=1))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "This report is an estimate based on keyword matching and AI analysis. "
        "It does not guarantee how a specific employer's ATS will score your resume.",
        styles["SmallGray"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
