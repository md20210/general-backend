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
    """Guess document type from filename or path"""
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
