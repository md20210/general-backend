"""Application Tracker Service - Document parsing and processing"""
import io
import zipfile
from typing import List, Tuple
from PyPDF2 import PdfReader
from docx import Document as DocxDocument


class DocumentParser:
    """Parse documents and extract text"""

    async def parse_file(self, filename: str, file_data: bytes) -> str:
        """Parse file and return extracted text"""
        filename_lower = filename.lower()

        if filename_lower.endswith('.pdf'):
            return self._parse_pdf(file_data)
        elif filename_lower.endswith('.docx'):
            return self._parse_docx(file_data)
        elif filename_lower.endswith('.txt'):
            return self._parse_txt(file_data)
        else:
            try:
                return file_data.decode('utf-8')
            except:
                return f"[Unable to parse {filename}]"

    def _parse_pdf(self, file_data: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = PdfReader(pdf_file)
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
            return "\n\n".join(text)
        except Exception as e:
            return f"[Error parsing PDF: {str(e)}]"

    def _parse_docx(self, file_data: bytes) -> str:
        """Extract text from DOCX"""
        try:
            docx_file = io.BytesIO(file_data)
            doc = DocxDocument(docx_file)
            text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text.append(paragraph.text)
            return "\n\n".join(text)
        except Exception as e:
            return f"[Error parsing DOCX: {str(e)}]"

    def _parse_txt(self, file_data: bytes) -> str:
        """Extract text from TXT"""
        try:
            return file_data.decode('utf-8')
        except UnicodeDecodeError:
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return file_data.decode(encoding)
                except:
                    continue
            return "[Unable to decode text file]"

    async def extract_zip(self, zip_data: bytes) -> List[Tuple[str, str, bytes]]:
        """Extract files from ZIP and return list of (path, filename, content)"""
        files = []
        try:
            with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_ref:
                file_list = [f for f in zip_ref.namelist() if not f.endswith('/')]
                for file_path in file_list:
                    try:
                        file_data = zip_ref.read(file_path)
                        filename = file_path.split('/')[-1]
                        files.append((file_path, filename, file_data))
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
                        continue
        except Exception as e:
            print(f"Error extracting ZIP: {e}")
        return files


def guess_doc_type(file_path: str) -> str:
    """Guess document type from filename or path (fallback only)"""
    file_path_lower = file_path.lower()

    if 'cv' in file_path_lower or 'lebenslauf' in file_path_lower or 'resume' in file_path_lower:
        return 'cv'
    elif 'cover' in file_path_lower or 'anschreiben' in file_path_lower or 'motivationsschreiben' in file_path_lower:
        return 'cover_letter'
    elif 'certificate' in file_path_lower or 'zeugnis' in file_path_lower or 'zertifikat' in file_path_lower:
        return 'certificate'
    elif 'transcript' in file_path_lower or 'notenuebersicht' in file_path_lower:
        return 'transcript'
    elif 'portfolio' in file_path_lower:
        return 'portfolio'
    else:
        return 'other'


def classify_document_with_llm(document_text: str, filename: str) -> str:
    """
    Classify document type using LLM content analysis

    Args:
        document_text: Extracted text from document
        filename: Document filename (for context)

    Returns:
        'cv', 'cover_letter', 'job_description', or 'other'
    """
    from backend.services.llm_gateway import llm_gateway

    # Use first 1500 chars for classification (enough to identify document type)
    text_sample = document_text[:1500]

    prompt = f"""Klassifiziere das folgende Dokument in GENAU EINE dieser Kategorien:
- cv (Lebenslauf/CV/Resume mit Berufserfahrung, Ausbildung, Skills)
- cover_letter (Anschreiben/Bewerbungsschreiben/Motivationsschreiben)
- job_description (Stellenausschreibung/Job Posting mit Anforderungen)
- other (Zeugnisse, Zertifikate, sonstige Dokumente)

Dateiname: {filename}

Dokumenteninhalt:
{text_sample}

Antworte NUR mit dem Kategorie-Namen (cv, cover_letter, job_description, oder other), keine Erklärungen."""

    try:
        result = llm_gateway.generate(
            prompt=prompt,
            provider="ollama",
            temperature=0.1,
            max_tokens=20
        )

        response_text = result.get('response', '').strip().lower()

        # Extract valid category from response
        if 'cv' in response_text or 'lebenslauf' in response_text or 'resume' in response_text:
            return 'cv'
        elif 'cover_letter' in response_text or 'anschreiben' in response_text or 'motivationsschreiben' in response_text:
            return 'cover_letter'
        elif 'job_description' in response_text or 'stellenausschreibung' in response_text:
            return 'job_description'
        else:
            return 'other'
    except Exception as e:
        print(f"LLM classification failed, using filename fallback: {e}")
        return guess_doc_type(filename)


def extract_application_info(documents_text: str) -> dict:
    """
    Extract company name and position from application documents using LLM

    Args:
        documents_text: Combined text from CV, cover letter, etc.

    Returns:
        dict with 'company_name' and 'position' (or None if not found)
    """
    from backend.services.llm_gateway import llm_gateway

    prompt = f"""Analysiere die folgenden Bewerbungsunterlagen und extrahiere:
1. Firmenname (Unternehmen, an das sich beworben wird)
2. Position/Jobtitel (z.B. "Senior Developer", "Product Manager")

Dokumente:
{documents_text[:2000]}

Antworte NUR im folgenden JSON-Format (keine zusätzlichen Erklärungen):
{{"company_name": "Firmenname oder null", "position": "Position oder null"}}
"""

    try:
        result = llm_gateway.generate(
            prompt=prompt,
            provider="ollama",  # Fast local model for extraction
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=100
        )

        # Parse JSON response from LLM
        import json
        response_text = result.get('response', '')

        # Extract JSON from response (in case there's extra text)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            parsed = json.loads(json_str)
            return {
                "company_name": parsed.get("company_name") if parsed.get("company_name") != "null" else None,
                "position": parsed.get("position") if parsed.get("position") != "null" else None
            }
    except Exception as e:
        print(f"LLM extraction failed: {e}")

    return {"company_name": None, "position": None}
