import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_txt_report(original, optimized, model, category, tone, length, score, why_better):
    """Generate a plain text optimization report."""
    why_better_text = ""
    if isinstance(why_better, dict):
        for k, v in why_better.items():
            why_better_text += f"- {k.capitalize()}: {v}\n"
    elif isinstance(why_better, str):
        why_better_text = why_better
        
    report = (
        "==================================================\n"
        "           PROMPT OPTIMIZATION REPORT             \n"
        "==================================================\n\n"
        f"Model: {model}\n"
        f"Category: {category}\n"
        f"Tone: {tone}\n"
        f"Length: {length}\n"
        f"Quality Score: {score}/100\n\n"
        "--------------------------------------------------\n"
        "ORIGINAL PROMPT:\n"
        "--------------------------------------------------\n"
        f"{original}\n\n"
        "--------------------------------------------------\n"
        "OPTIMIZED PROMPT:\n"
        "--------------------------------------------------\n"
        f"{optimized}\n\n"
        "--------------------------------------------------\n"
        "WHY IT IS BETTER:\n"
        "--------------------------------------------------\n"
        f"{why_better_text}\n"
        "==================================================\n"
    )
    return report

def generate_pdf_report(original, optimized, model, category, tone, length, score, score_details, why_better):
    """
    Generate a professional PDF optimization report using ReportLab.
    Returns a bytes buffer containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Palette (Premium Indigo / Slate Theme)
    primary_color = colors.HexColor("#6366F1")  # Indigo
    secondary_color = colors.HexColor("#0F172A")  # Slate 900
    text_color = colors.HexColor("#334155")  # Slate 700
    light_bg = colors.HexColor("#F8FAFC")  # Slate 50
    border_color = colors.HexColor("#E2E8F0")  # Slate 200
    
    # Custom Paragraph Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=secondary_color,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'BulletItem',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    elements = []
    
    # 1. Header Band
    elements.append(Paragraph("Prompt Optimizer AI", title_style))
    elements.append(Paragraph("Professional Prompt Enhancement & Analysis Report", subtitle_style))
    elements.append(Spacer(1, 10))
    
    # 2. Metadata Table
    metadata_data = [
        [
            Paragraph("<b>Target Model:</b>", body_style), Paragraph(model, body_style),
            Paragraph("<b>Optimization Score:</b>", body_style), Paragraph(f"<b>{score}/100</b>", body_style)
        ],
        [
            Paragraph("<b>Category:</b>", body_style), Paragraph(category, body_style),
            Paragraph("<b>Tone:</b>", body_style), Paragraph(tone, body_style)
        ],
        [
            Paragraph("<b>Output Length:</b>", body_style), Paragraph(length, body_style),
            Paragraph("", body_style), Paragraph("", body_style)
        ]
    ]
    
    meta_table = Table(metadata_data, colWidths=[1.2*inch, 2.2*inch, 1.6*inch, 1.5*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, border_color),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 20))
    
    # 3. Score Breakdown (if available)
    if score_details:
        elements.append(Paragraph("Quality Metrics", h1_style))
        metrics_headers = []
        metrics_scores = []
        for metric, val in score_details.items():
            metrics_headers.append(Paragraph(f"<b>{metric.capitalize()}</b>", body_style))
            metrics_scores.append(Paragraph(f"{val}/100", body_style))
            
        metrics_table_data = [metrics_headers, metrics_scores]
        metrics_table = Table(metrics_table_data, colWidths=[1.3*inch]*len(score_details))
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EEF2F6")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
    # 4. Original Prompt
    elements.append(Paragraph("Original Prompt", h1_style))
    orig_paragraphs = [Paragraph(p.replace('\n', '<br/>'), body_style) for p in original.split('\n\n') if p.strip()]
    orig_table = Table([[orig_paragraphs]], colWidths=[6.5*inch])
    orig_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#FEF2F2")), # Light Red Tint
        ('PADDING', (0,0), (0,0), 10),
        ('BOX', (0,0), (0,0), 1, colors.HexColor("#FCA5A5")),
    ]))
    elements.append(orig_table)
    elements.append(Spacer(1, 20))
    
    # 5. Optimized Prompt
    elements.append(Paragraph("Optimized Prompt", h1_style))
    opt_paragraphs = [Paragraph(p.replace('\n', '<br/>'), code_style) for p in optimized.split('\n\n') if p.strip()]
    opt_table = Table([[opt_paragraphs]], colWidths=[6.5*inch])
    opt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#ECFDF5")), # Light Green Tint
        ('PADDING', (0,0), (0,0), 12),
        ('BOX', (0,0), (0,0), 1.5, colors.HexColor("#A7F3D0")),
    ]))
    elements.append(opt_table)
    elements.append(Spacer(1, 20))
    
    # 6. Why It Is Better
    elements.append(Paragraph("Why It Is Better", h1_style))
    if isinstance(why_better, dict):
        for category, explanation in why_better.items():
            bullet_text = f"<b>&bull; {category.capitalize()}:</b> {explanation}"
            elements.append(Paragraph(bullet_text, bullet_style))
    elif isinstance(why_better, str):
        elements.append(Paragraph(why_better, body_style))
        
    # Build Document
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
