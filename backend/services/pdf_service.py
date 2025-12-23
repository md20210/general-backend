"""PDF Report Generation Service for CV Matcher."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from typing import List, Dict, Any
from datetime import datetime


class PDFReportService:
    """Service for generating PDF reports from match results and chat history."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=20,
            alignment=1,  # Center
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceBefore=15,
            spaceAfter=10,
        ))

        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#4b5563'),
        ))

        # Chat message style
        self.styles.add(ParagraphStyle(
            name='ChatMessage',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=13,
            leftIndent=10,
            rightIndent=10,
            textColor=colors.HexColor('#1f2937'),
        ))

    def generate_match_report(
        self,
        match_result: Dict[str, Any],
        chat_history: List[Dict[str, Any]] = None
    ) -> BytesIO:
        """
        Generate PDF report for CV match analysis.

        Args:
            match_result: Dictionary containing match analysis results
            chat_history: List of chat messages [{"role": "user"|"assistant", "content": str, "timestamp": str}]

        Returns:
            BytesIO: PDF file as bytes
        """
        buffer = BytesIO()

        # Use landscape orientation for wider tables
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )

        # Build PDF content
        elements = []

        # Title
        elements.append(Paragraph("CV Match Analysis Report", self.styles['CustomTitle']))
        elements.append(Paragraph(
            f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Overall Score
        score = match_result.get('overallScore', 0)
        elements.append(Paragraph("Overall Match Score", self.styles['CustomHeading']))
        elements.append(Paragraph(
            f"<b><font size=20 color={'#10b981' if score >= 70 else '#f59e0b' if score >= 40 else '#ef4444'}>{score}%</font></b>",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Strengths and Gaps (2-column layout)
        elements.append(Paragraph("Strengths & Gaps", self.styles['CustomHeading']))

        strengths = match_result.get('strengths', [])
        gaps = match_result.get('gaps', [])

        # Create side-by-side table
        max_items = max(len(strengths), len(gaps))
        data = [['<b>Strengths</b>', '<b>Gaps</b>']]

        for i in range(max_items):
            strength = f"✓ {strengths[i]}" if i < len(strengths) else ""
            gap = f"⚠ {gaps[i]}" if i < len(gaps) else ""
            data.append([strength, gap])

        table = Table(data, colWidths=[12*cm, 12*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f0fdf4')),
            ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#fef2f2')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))

        # Recommendations
        recommendations = match_result.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Recommendations", self.styles['CustomHeading']))
            for rec in recommendations:
                elements.append(Paragraph(f"→ {rec}", self.styles['CustomBody']))
                elements.append(Spacer(1, 0.2*cm))
            elements.append(Spacer(1, 0.3*cm))

        # Comparison Table (if available)
        comparison = match_result.get('comparison', [])
        if comparison:
            elements.append(PageBreak())
            elements.append(Paragraph("Detailed Comparison", self.styles['CustomHeading']))

            comp_data = [['Requirement', 'Applicant Match', 'Level', 'Confidence']]
            for comp in comparison:
                level_text = {
                    'full': 'Vollständig',
                    'partial': 'Teilweise',
                    'missing': 'Fehlend'
                }.get(comp.get('match_level', ''), comp.get('match_level', ''))

                comp_data.append([
                    comp.get('requirement', ''),
                    comp.get('applicant_match', ''),
                    level_text,
                    f"{comp.get('confidence', 0)}%"
                ])

            comp_table = Table(comp_data, colWidths=[8*cm, 8*cm, 4*cm, 3*cm])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(comp_table)
            elements.append(Spacer(1, 0.5*cm))

        # Detailed Analysis
        detailed = match_result.get('detailedAnalysis', '')
        if detailed:
            elements.append(Paragraph("Detailed Analysis", self.styles['CustomHeading']))
            elements.append(Paragraph(detailed.replace('\n', '<br/>'), self.styles['CustomBody']))
            elements.append(Spacer(1, 0.5*cm))

        # Chat History
        if chat_history and len(chat_history) > 0:
            elements.append(PageBreak())
            elements.append(Paragraph("Chat History", self.styles['CustomHeading']))
            elements.append(Paragraph(
                "Below are the questions asked and answers provided during the analysis session.",
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 0.5*cm))

            for msg in chat_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')

                # Role header with timestamp
                role_text = "👤 User" if role == "user" else "🤖 Assistant"
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt.strftime('%H:%M')
                        role_text += f" ({time_str})"
                    except:
                        pass

                elements.append(Paragraph(
                    f"<b>{role_text}</b>",
                    self.styles['CustomBody']
                ))

                # Message content
                bg_color = colors.HexColor('#eff6ff') if role == 'user' else colors.HexColor('#f9fafb')

                # Create message box
                msg_data = [[content.replace('\n', '<br/>')]]
                msg_table = Table(msg_data, colWidths=[24*cm])
                msg_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('PADDING', (0, 0), (-1, -1), 10),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
                ]))
                elements.append(msg_table)
                elements.append(Spacer(1, 0.3*cm))

        # Build PDF
        doc.build(elements)

        buffer.seek(0)
        return buffer


# Global instance
pdf_service = PDFReportService()
