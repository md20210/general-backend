"""LifeChronicle Service - Timeline management and LLM processing."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from io import BytesIO

from backend.services.llm_gateway import llm_gateway
from backend.services.pdf_service import pdf_service


class LifeChronicleService:
    """Service for managing life timeline entries."""

    def __init__(self):
        # In-memory storage for MVP (later: PostgreSQL)
        self.entries: Dict[str, Dict[str, Any]] = {}
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Initialize with demo timeline for test user."""
        demo_entries = [
            {
                "date": "1985-06-15",
                "original_text": "Ich wurde in München geboren. Ein sonniger Sommertag, wie mir meine Mutter später erzählte.",
                "status": "processed",
                "processed_text": "An einem strahlenden Junitag des Jahres 1985 erblickte ich in der bayerischen Hauptstadt München das Licht der Welt. Die Sonne schien warm durch die Fenster des Krankenhauses, während meine Eltern voller Freude ihr erstes Kind in den Armen hielten. Es war der Beginn einer Reise, die mich durch viele Höhen und Tiefen führen sollte."
            },
            {
                "date": "1990-09-01",
                "original_text": "Mein erster Schultag. Ich war aufgeregt und hatte eine riesige Schultüte dabei.",
                "status": "pending"
            },
            {
                "date": "1998-06-20",
                "original_text": "Abitur bestanden! Notendurchschnitt 1,8. Wir haben die ganze Nacht gefeiert.",
                "status": "pending"
            },
            {
                "date": "2003-10-01",
                "original_text": "Erste Stelle bei Siemens als Junior Software Engineer. Endlich im Berufsleben!",
                "status": "processed",
                "processed_text": "Mit einem Gefühl der Aufregung und Erwartung betrat ich am 1. Oktober 2003 zum ersten Mal die Büroräume von Siemens. Als frischgebackener Junior Software Engineer begann hier meine professionelle Karriere. Die imposanten Gebäude, die geschäftigen Kollegen und die moderne Technologie – alles fühlte sich gleichzeitig fremd und faszinierend an. Dies war der Moment, in dem aus dem Studenten ein Berufstätiger wurde."
            },
            {
                "date": "2010-07-15",
                "original_text": "Hochzeit mit meiner Frau Sarah. Der schönste Tag meines Lebens!",
                "status": "pending"
            },
            {
                "date": "2015-03-01",
                "original_text": "Beförderung zum Senior Projektleiter. Verantwortung für ein Team von 12 Entwicklern.",
                "status": "pending"
            },
            {
                "date": "2020-05-20",
                "original_text": "Unser erstes Kind wurde geboren - Emma Sophie. 3.450g, 52cm. Gesund und munter.",
                "status": "pending"
            },
            {
                "date": "2023-11-01",
                "original_text": "Neuer Job bei IBM als Principal AI Consultant. Spannende Herausforderungen warten!",
                "status": "pending"
            },
        ]

        for entry_data in demo_entries:
            entry_id = str(uuid.uuid4())
            self.entries[entry_id] = {
                "id": entry_id,
                "date": entry_data["date"],
                "original_text": entry_data["original_text"],
                "processed_text": entry_data.get("processed_text"),
                "status": entry_data["status"],
                "created_at": datetime.now().isoformat()
            }

    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all timeline entries sorted by date."""
        entries = list(self.entries.values())
        # Sort by date (newest first)
        entries.sort(key=lambda x: x['date'], reverse=True)
        return entries

    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get single entry by ID."""
        return self.entries.get(entry_id)

    def create_entry(self, date: str, original_text: str) -> Dict[str, Any]:
        """Create new timeline entry."""
        if not date or not original_text:
            raise ValueError("Date and text are required")

        entry_id = str(uuid.uuid4())
        entry = {
            "id": entry_id,
            "date": date,
            "original_text": original_text.strip(),
            "processed_text": None,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        self.entries[entry_id] = entry
        return entry

    def delete_entry(self, entry_id: str) -> bool:
        """Delete entry by ID."""
        if entry_id in self.entries:
            del self.entries[entry_id]
            return True
        return False

    async def process_with_llm(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """
        Process entry with local LLM to create literary book chapter.

        Uses Ollama (llama3 or mistral) to transform raw text
        into beautifully written prose.
        """
        entry = self.get_entry(entry_id)
        if not entry:
            return None

        # Create prompt for LLM
        prompt = f"""Du bist ein professioneller Autobiografie-Autor.

Verwandle die folgende persönliche Erinnerung in ein literarisches Buchkapitel.
Schreibe in der Ich-Form, emotional und lebendig. Füge sensorische Details hinzu.
Länge: 3-5 Sätze.

Datum: {entry['date']}
Erinnerung: {entry['original_text']}

Buchkapitel:"""

        # Process with local LLM (Ollama)
        try:
            result = await llm_gateway.generate(
                prompt=prompt,
                provider="ollama",
                model="llama3",
                temperature=0.7,
                max_tokens=300
            )

            processed_text = result.get('content', '').strip()

            # Update entry
            entry['processed_text'] = processed_text
            entry['status'] = 'processed'
            self.entries[entry_id] = entry

            return entry

        except Exception as e:
            print(f"LLM processing error: {e}")
            raise

    async def export_as_pdf(self) -> BytesIO:
        """
        Export entire timeline as PDF book.

        Creates beautifully formatted PDF with:
        - Title page
        - Table of contents
        - Chronological chapters
        - Uses processed text where available
        """
        # Get all entries sorted chronologically (oldest first for book)
        entries = list(self.entries.values())
        entries.sort(key=lambda x: x['date'])

        # Prepare data for PDF service
        timeline_data = {
            "title": "Meine Lebensgeschichte",
            "subtitle": "Eine persönliche Chronik",
            "entries": entries
        }

        # Generate PDF using existing PDF service
        # (We'll extend pdf_service to support timeline format)
        pdf_buffer = await self._generate_timeline_pdf(timeline_data)

        return pdf_buffer

    async def _generate_timeline_pdf(self, data: Dict[str, Any]) -> BytesIO:
        """Generate PDF for timeline data."""
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib import colors

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        elements = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=10,
            alignment=1  # Center
        )
        elements.append(Paragraph(data['title'], title_style))
        elements.append(Paragraph(data['subtitle'], styles['Normal']))
        elements.append(Spacer(1, 2*cm))

        # Entries
        for entry in data['entries']:
            # Date header
            date_str = entry['date']
            try:
                date_obj = datetime.fromisoformat(entry['date'])
                date_str = date_obj.strftime('%d. %B %Y')
            except:
                pass

            elements.append(Paragraph(f"<b>📅 {date_str}</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.3*cm))

            # Text (use processed if available)
            text = entry.get('processed_text') or entry['original_text']
            elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 0.8*cm))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer


# Global instance
lifechonicle_service = LifeChronicleService()
