# LifeChronicle Service - Dokumentation

## Überblick

Der LifeChronicle Service ist ein Backend-Service für die Timeline-Verwaltung mit KI-gestützter Textveredelung und PDF-Export.

**Datei:** `backend/services/lifechonicle_service.py`

## Funktionsweise

### 1. In-Memory Storage (MVP)

```python
class LifeChronicleService:
    def __init__(self):
        # In-memory storage für Timeline-Einträge
        self.entries: Dict[str, Dict[str, Any]] = {}
        # Demo-Daten beim Start laden
        self._initialize_demo_data()
```

**Einschränkungen:**
- Daten gehen bei Server-Restart verloren
- Kein Multi-User-Support
- Maximal ~1000 Einträge empfohlen

**Geplante Migration:** PostgreSQL (Phase 2)

### 2. Demo-Daten

**8 vorausgefüllte Einträge:**
1. Geburt (1985) - ✅ processed
2. Erster Schultag (1990) - ⏸️ pending
3. Abitur (1998) - ⏸️ pending
4. Berufseinstieg (2003) - ✅ processed
5. Hochzeit (2010) - ⏸️ pending
6. Beförderung (2015) - ⏸️ pending
7. Vater geworden (2020) - ⏸️ pending
8. Neuer Job (2023) - ⏸️ pending

**Zweck:**
- Sofortige Demonstration der Funktionalität
- Keine Registrierung notwendig (MVP)
- Showcase-Zwecke

## API-Methoden

### 1. get_all_entries()

```python
def get_all_entries(self) -> List[Dict[str, Any]]:
    """Get all timeline entries sorted by date (newest first)."""
    entries = list(self.entries.values())
    entries.sort(key=lambda x: x['date'], reverse=True)
    return entries
```

**Sortierung:** Neueste zuerst (descending)
**Return:** Liste von Entry-Dictionaries

### 2. get_entry(entry_id)

```python
def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
    """Get single entry by ID."""
    return self.entries.get(entry_id)
```

**Return:** Entry oder None (wenn nicht gefunden)

### 3. create_entry(title, date, original_text)

```python
def create_entry(self, title: str, date: str, original_text: str) -> Dict[str, Any]:
    """Create new timeline entry."""
    if not title or not date or not original_text:
        raise ValueError("Title, date and text are required")

    entry_id = str(uuid.uuid4())
    entry = {
        "id": entry_id,
        "title": title.strip(),
        "date": date,
        "original_text": original_text.strip(),
        "processed_text": None,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }

    self.entries[entry_id] = entry
    return entry
```

**Validation:**
- `title`: String, nicht leer
- `date`: String (ISO 8601 Format empfohlen)
- `original_text`: String, nicht leer

**Return:** Neu erstellter Entry mit UUID

### 4. delete_entry(entry_id)

```python
def delete_entry(self, entry_id: str) -> bool:
    """Delete entry by ID."""
    if entry_id in self.entries:
        del self.entries[entry_id]
        return True
    return False
```

**Return:**
- `True` - Erfolgreich gelöscht
- `False` - Entry nicht gefunden

### 5. process_with_llm(entry_id, provider)

```python
async def process_with_llm(
    self,
    entry_id: str,
    provider: str = "ollama"
) -> Optional[Dict[str, Any]]:
    """
    Process entry with LLM to create literary book chapter.

    Args:
        entry_id: ID of entry to process
        provider: LLM provider ("ollama", "grok", or "anthropic")

    Uses Ollama (local, DSGVO-compliant), GROK, or Anthropic Claude.
    """
```

**LLM-Provider:**
1. **Ollama (default, DSGVO-konform)**
   - Model: `qwen2.5:3b`
   - Temperature: 0.7
   - Max Tokens: 300
   - Lokal auf Railway

2. **GROK (cloud-basiert)**
   - Model: `grok-3`
   - Temperature: 0.7
   - Max Tokens: 300
   - xAI API

3. **Anthropic (optional)**
   - Model: `claude-sonnet-3-5-20241022`
   - Temperature: 0.7
   - Max Tokens: 300

**Prompt-Template:**
```python
prompt = f"""Du bist ein professioneller Autobiografie-Autor.

Verwandle die folgende persönliche Erinnerung in ein literarisches Buchkapitel.
Schreibe in der Ich-Form, emotional und lebendig. Füge sensorische Details hinzu.
Länge: 3-5 Sätze.

Datum: {entry['date']}
Erinnerung: {entry['original_text']}

Buchkapitel:"""
```

**Return:** Updated Entry mit `processed_text` und `status="processed"`

**Error Handling:**
```python
try:
    result = llm_gateway.generate(...)
    processed_text = result.get('response', '').strip()

    entry['processed_text'] = processed_text
    entry['status'] = 'processed'
    self.entries[entry_id] = entry

    return entry

except Exception as e:
    print(f"LLM processing error: {e}")
    raise
```

### 6. export_as_pdf()

```python
async def export_as_pdf(self) -> BytesIO:
    """
    Export entire timeline as PDF book.

    Creates beautifully formatted PDF with:
    - Title page
    - Table of contents (future)
    - Chronological chapters
    - Uses processed text where available
    - Timeline colors (6-color palette)
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

    # Generate PDF with timeline colors
    pdf_buffer = await self._generate_timeline_pdf(timeline_data)

    return pdf_buffer
```

**Sortierung:** Älteste zuerst (ascending) - chronologische Reihenfolge
**Return:** BytesIO Buffer mit PDF-Daten

## PDF-Generierung

### Timeline Color Palette

```python
TIMELINE_COLORS = [
    {'bg': '#e9d5ff', 'border': '#c084fc', 'text': '#581c87'},  # Purple
    {'bg': '#ccfbf1', 'border': '#5eead4', 'text': '#134e4a'},  # Teal
    {'bg': '#d1fae5', 'border': '#6ee7b7', 'text': '#065f46'},  # Green
    {'bg': '#fef3c7', 'border': '#fcd34d', 'text': '#78350f'},  # Yellow
    {'bg': '#fed7aa', 'border': '#fdba74', 'text': '#7c2d12'},  # Orange
    {'bg': '#fce7f3', 'border': '#f9a8d4', 'text': '#831843'},  # Pink
]
```

**Cycling:** `color_set = TIMELINE_COLORS[idx % len(TIMELINE_COLORS)]`

### ReportLab PDF-Struktur

```python
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors

buffer = BytesIO()
doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
```

**Seiten-Setup:**
- Format: A4 Portrait
- Top Margin: 2 cm
- Bottom Margin: 2 cm
- Seitengröße: 595 x 842 Punkte

### Title Page

```python
# Title
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=28,
    textColor=colors.HexColor('#14b8a6'),  # Teal
    spaceAfter=10,
    alignment=1  # Center
)
elements.append(Paragraph(data['title'], title_style))
elements.append(Paragraph(data['subtitle'], styles['Normal']))
elements.append(Spacer(1, 2*cm))
```

### Entry Tables (Colored)

```python
for idx, entry in enumerate(data['entries']):
    # Get color for this entry
    color_set = TIMELINE_COLORS[idx % len(TIMELINE_COLORS)]

    # Entry title with colored background
    title_style_colored = ParagraphStyle(
        f'ColoredTitle{idx}',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor(color_set['text']),
        spaceAfter=6,
        leftIndent=10
    )

    # Create colored box for entry
    entry_title = Paragraph(f"<b>{entry['title']} ({date_str})</b>", title_style_colored)

    # Text (use processed if available)
    text = entry.get('processed_text') or entry['original_text']
    text_style = ParagraphStyle(
        f'EntryText{idx}',
        parent=styles['Normal'],
        leftIndent=10,
        rightIndent=10,
        spaceBefore=6,
        spaceAfter=12
    )
    entry_text = Paragraph(text, text_style)

    # Create table with colored border
    table_data = [[entry_title], [entry_text]]
    table = Table(table_data, colWidths=[15*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor(color_set['bg'])),
        ('LINEABOVE', (0, 0), (-1, 0), 3, colors.HexColor(color_set['border'])),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.HexColor(color_set['border'])),
        ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor(color_set['border'])),
        ('LINEAFTER', (-1, 0), (-1, -1), 1, colors.HexColor(color_set['border'])),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.8*cm))
```

**Table Styling:**
- **Background:** Title row mit Timeline-Farbe
- **Borders:**
  - Top: 3px in Timeline-Farbe
  - Left: 3px in Timeline-Farbe (prominent)
  - Bottom: 1px in Timeline-Farbe
  - Right: 1px in Timeline-Farbe
- **Padding:** 10-12px für Lesbarkeit
- **Spacing:** 0.8cm zwischen Entries

### Build PDF

```python
# Build PDF
doc.build(elements)
buffer.seek(0)
return buffer
```

## Performance

### LLM Processing

**Ollama (qwen2.5:3b):**
- CPU-basiert: 10-30 Sekunden
- DSGVO-konform
- Kostenlos

**GROK (grok-3):**
- Cloud-basiert: 2-5 Sekunden
- Schneller
- Kostenpflichtig

### PDF Generation

**Metriken:**
- 8 Einträge: ~2-3 Sekunden
- Dateigröße: 50-200 KB
- ReportLab Performance: Sehr effizient

## Fehlerbehandlung

### Entry Not Found

```python
if entry_id not in self.entries:
    raise HTTPException(status_code=404, detail="Entry not found")
```

### Validation Errors

```python
if not title or not date or not original_text:
    raise ValueError("Title, date and text are required")
```

### LLM Errors

```python
except Exception as e:
    print(f"LLM processing error: {e}")
    raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
```

## Zukünftige Verbesserungen

### Database Integration

```python
# Future: PostgreSQL statt In-Memory
from sqlalchemy import Column, String, Text, DateTime, Enum
from backend.models.base import Base

class LifeChronicleEntry(Base):
    __tablename__ = "lifechonicle_entries"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    title = Column(String, nullable=False)
    date = Column(String, nullable=False)
    original_text = Column(Text, nullable=False)
    processed_text = Column(Text, nullable=True)
    status = Column(Enum('pending', 'processed'), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Caching

```python
# Future: Redis für processed entries
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

def get_entry_cached(entry_id: str):
    cached = r.get(f"entry:{entry_id}")
    if cached:
        return json.loads(cached)
    entry = self.get_entry(entry_id)
    r.setex(f"entry:{entry_id}", 3600, json.dumps(entry))
    return entry
```

### Multi-User Support

```python
# Future: User-spezifische Timelines
def get_user_entries(user_id: str) -> List[Dict[str, Any]]:
    return db.query(LifeChronicleEntry)\
             .filter(LifeChronicleEntry.user_id == user_id)\
             .order_by(LifeChronicleEntry.date.desc())\
             .all()
```

## Testing

### Unit Tests (geplant)

```python
import pytest
from backend.services.lifechonicle_service import lifechonicle_service

def test_create_entry():
    entry = lifechonicle_service.create_entry(
        title="Test Event",
        date="2024-12-25",
        original_text="This is a test event."
    )
    assert entry['title'] == "Test Event"
    assert entry['status'] == "pending"

def test_delete_entry():
    entry = lifechonicle_service.create_entry(...)
    result = lifechonicle_service.delete_entry(entry['id'])
    assert result is True
```

---

**Letzte Aktualisierung:** 2024-12-25
**Version:** 1.0.1
**Datei:** `backend/services/lifechonicle_service.py`
