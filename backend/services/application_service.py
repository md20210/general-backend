"""Application Tracker Service - Document parsing and processing"""
import io
import zipfile
import numpy as np
from typing import List, Tuple, Literal
from PyPDF2 import PdfReader
from docx import Document as DocxDocument

# Optional OCR imports
try:
    from PIL import Image
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from paddleocr import PaddleOCR, PPStructure
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False


# Global PaddleOCR instances (singleton to avoid re-initialization error)
_paddle_ocr_instance = None
_paddle_structure_instance = None


def get_paddle_ocr():
    """Get or create PaddleOCR singleton instance"""
    global _paddle_ocr_instance
    if _paddle_ocr_instance is None and PADDLE_AVAILABLE:
        try:
            _paddle_ocr_instance = PaddleOCR(use_angle_cls=True, lang='latin', use_gpu=False)
        except Exception as e:
            print(f"Failed to initialize PaddleOCR: {e}")
    return _paddle_ocr_instance


def get_paddle_structure():
    """Get or create PPStructure singleton instance"""
    global _paddle_structure_instance
    if _paddle_structure_instance is None and PADDLE_AVAILABLE:
        try:
            _paddle_structure_instance = PPStructure(table=True, ocr=True, lang='latin', recovery=True, use_gpu=False)
        except Exception as e:
            print(f"Failed to initialize PPStructure: {e}")
    return _paddle_structure_instance


def deskew_image(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Deskew an image using projection profile method.

    Args:
        image: Grayscale image as numpy array

    Returns:
        Tuple of (deskewed image, detected angle in degrees)
    """
    if not CV2_AVAILABLE:
        return image, 0.0

    # Binarize image
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Find coordinates of all white pixels
    coords = np.column_stack(np.where(thresh > 0))

    if len(coords) < 100:
        # Not enough points, return original
        return image, 0.0

    # Calculate skew angle using minAreaRect
    angle = cv2.minAreaRect(coords)[-1]

    # Normalize angle
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    # Only correct if angle is significant (> 0.5 degrees)
    if abs(angle) < 0.5:
        return image, 0.0

    # Rotate image to deskew
    (h, w) = image.shape
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return deskewed, angle


def get_ocr_quality(image: np.ndarray) -> float:
    """
    Measure OCR quality/confidence on an image.

    Args:
        image: Grayscale image as numpy array

    Returns:
        Average OCR confidence (0-100%)
    """
    if not TESSERACT_AVAILABLE:
        return 0.0

    try:
        from PIL import Image as PILImage
        pil_img = PILImage.fromarray(image)

        # Use European languages for quality measurement (same as rotation detection)
        european_langs = 'deu+eng+spa+fra+ita+pol+ces+nld+por+ron+hun+slk+slv+hrv+bul+ell+swe+dan+nor+fin'

        # Get detailed OCR data with confidence scores
        data = pytesseract.image_to_data(pil_img, lang=european_langs, output_type=pytesseract.Output.DICT)

        # Calculate average confidence for all recognized words
        confidences = [int(conf) for conf in data['conf'] if conf != '-1' and int(conf) > 0]

        if len(confidences) == 0:
            return 0.0

        avg_confidence = sum(confidences) / len(confidences)
        return avg_confidence

    except Exception as e:
        print(f"Failed to measure OCR quality: {e}")
        return 0.0


def detect_and_correct_rotation(image_path: str) -> Tuple[np.ndarray, float, float]:
    """
    Automatic rotation correction for 0°/90°/180°/270° + deskewing.

    Smart algorithm:
    1. Test original image first - if quality ≥90%, skip rotation testing (performance optimization)
    2. Otherwise test all rotations using OCR on grayscale
    3. Apply best rotation to ORIGINAL COLOR image
    4. Then deskewing for slight angle correction
    5. Measures both original and final OCR quality (0-100%)

    Args:
        image_path: Path to the image file

    Returns:
        Tuple of (corrected COLOR image as numpy array BGR, original OCR quality %, processed OCR quality %)
    """
    if not CV2_AVAILABLE:
        # Fallback: Return PIL image as numpy array
        img = Image.open(image_path).convert('RGB')
        return np.array(img), 0.0, 0.0

    # Read ORIGINAL COLOR IMAGE
    img_color = cv2.imread(image_path)
    if img_color is None:
        # Fallback to PIL
        img = Image.open(image_path).convert('RGB')
        return np.array(img), 0.0, 0.0

    # Work with grayscale for rotation detection
    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)  # Reduce noise

    # ALWAYS test ALL 4 rotations to find the best one
    # CRITICAL: High OCR quality does NOT guarantee correct orientation!
    # Example: Invoice rotated 180° can have 91% OCR (numbers readable upside-down)
    # The ONLY way to ensure correct orientation: test all rotations and pick best score
    print("Testing all 4 rotations to find best orientation...")

    best_img = gray
    best_score = -1
    best_angle = 0
    original_score = 0
    original_img = gray
    original_quality = 0

    for rot in [0, 90, 180, 270]:
        # Rotate image
        if rot == 0:
            rotated = gray
        elif rot == 90:
            rotated = cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE)
        elif rot == 180:
            rotated = cv2.rotate(gray, cv2.ROTATE_180)
        elif rot == 270:
            rotated = cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Calculate score: text length
        score = 0

        if TESSERACT_AVAILABLE:
            try:
                from PIL import Image as PILImage
                pil_img = PILImage.fromarray(rotated)
                # Use European languages for rotation detection (same as final OCR)
                european_langs = 'deu+eng+spa+fra+ita+pol+ces+nld+por+ron+hun+slk+slv+hrv+bul+ell+swe+dan+nor+fin'

                # Get both text length AND confidence
                data = pytesseract.image_to_data(pil_img, lang=european_langs, output_type=pytesseract.Output.DICT)

                # Calculate average confidence for recognized words
                confidences = [int(conf) for conf in data['conf'] if conf != '-1' and int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if len(confidences) > 0 else 0

                # Get text for character count
                text = pytesseract.image_to_string(pil_img, lang=european_langs, config='--psm 1')
                char_count = len(''.join(c for c in text if c.isalnum()))

                # Combined score: character count weighted by confidence
                # High confidence + many chars = best score
                score = char_count * (avg_confidence / 100.0)

                print(f"Rotation {rot}°: {char_count} chars, {avg_confidence:.1f}% conf, score={score:.1f}")
            except Exception as e:
                print(f"Rotation {rot}°: OCR failed ({e})")
                score = 0

        # Track scores for all rotations
        if rot == 0:
            original_score = score
            original_img = rotated
            # Measure original OCR quality for display
            original_quality = get_ocr_quality(rotated)

        if score > best_score:
            best_score = score
            best_img = rotated
            best_angle = rot

    # Prefer original orientation unless another rotation is SIGNIFICANTLY better
    # Threshold: 20% better score needed to rotate
    if original_score > 0 and best_angle != 0:
        improvement = (best_score - original_score) / original_score
        if improvement < 0.20:  # Less than 20% improvement
            print(f"⚠ Rotation {best_angle}° only {improvement*100:.1f}% better - keeping original (0°)")
            best_angle = 0
            best_img = original_img
            best_score = original_score

    print(f"✓ Best rotation: {best_angle}° (score={best_score:.1f})")

    # Apply the SAME rotation to the COLOR image
    if best_angle == 0:
        final_img_color = img_color
    elif best_angle == 90:
        final_img_color = cv2.rotate(img_color, cv2.ROTATE_90_CLOCKWISE)
    elif best_angle == 180:
        final_img_color = cv2.rotate(img_color, cv2.ROTATE_180)
    elif best_angle == 270:
        final_img_color = cv2.rotate(img_color, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        final_img_color = img_color

    # Apply deskewing to the grayscale (for OCR quality measurement)
    final_img_gray = best_img
    try:
        deskewed_gray, skew_angle = deskew_image(best_img)
        print(f"Deskew angle: {skew_angle:.2f}°")
        final_img_gray = deskewed_gray

        # Also apply same deskew to color image
        if abs(skew_angle) > 0.5:
            gray_for_color = cv2.cvtColor(final_img_color, cv2.COLOR_BGR2GRAY)
            (h, w) = gray_for_color.shape
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
            final_img_color = cv2.warpAffine(final_img_color, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    except Exception as e:
        print(f"Deskew failed: {e}")

    # Measure final OCR quality (on grayscale)
    processed_quality = get_ocr_quality(final_img_gray)
    print(f"Processed OCR Quality: {processed_quality:.1f}%")

    return final_img_color, original_quality, processed_quality


class DocumentParser:
    """Parse documents and extract text"""

    def __init__(self):
        # Use singleton instances to avoid re-initialization errors
        self.paddle_ocr = get_paddle_ocr() if PADDLE_AVAILABLE else None
        self.paddle_structure = get_paddle_structure() if PADDLE_AVAILABLE else None

    def parse(self, file_path: str, ocr_engine: Literal['tesseract', 'paddle'] = 'tesseract') -> str:
        """Parse file from path and return extracted text

        Args:
            file_path: Path to the file
            ocr_engine: OCR engine to use ('tesseract' or 'paddle')
        """
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Get filename from path
            filename = file_path.split('/')[-1]

            # Check if it's an image
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
                return self._parse_image(file_data, file_path, ocr_engine)

            # Use existing parse_file method
            import asyncio
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.parse_file(filename, file_data))
        except Exception as e:
            return f"[Error parsing file: {str(e)}]"

    def _parse_image(self, file_data: bytes, file_path: str = None, ocr_engine: str = 'tesseract') -> str:
        """Extract text from image using OCR

        Args:
            file_data: Image file bytes
            file_path: Optional file path for rotation correction
            ocr_engine: OCR engine to use ('tesseract' or 'paddle')
        """
        if ocr_engine == 'paddle':
            return self._parse_image_paddle(file_path or file_data)
        else:
            return self._parse_image_tesseract(file_data, file_path)

    def _parse_image_tesseract(self, file_data: bytes, file_path: str = None) -> str:
        """Extract text from image using Tesseract OCR with automatic rotation correction"""
        if not TESSERACT_AVAILABLE:
            return "[Tesseract OCR not available - Pillow/pytesseract not installed]"

        try:
            # Apply rotation correction if file_path is available and OpenCV is installed
            if file_path and CV2_AVAILABLE:
                try:
                    corrected_array, _, _ = detect_and_correct_rotation(file_path)
                    image = Image.fromarray(corrected_array)
                except Exception as rot_err:
                    # If rotation correction fails, fall back to original image
                    print(f"Rotation correction failed, using original: {rot_err}")
                    image = Image.open(io.BytesIO(file_data))
            else:
                image = Image.open(io.BytesIO(file_data))

            # Use all European languages for OCR (covers all EU invoices)
            # Priority: German, English, Spanish, French, Italian, Polish, Czech, Dutch, Portuguese
            european_langs = 'deu+eng+spa+fra+ita+pol+ces+nld+por+ron+hun+slk+slv+hrv+bul+ell+swe+dan+nor+fin'
            try:
                text = pytesseract.image_to_string(image, lang=european_langs)
            except Exception as tess_err:
                # Fallback: Try common languages if full list fails
                try:
                    text = pytesseract.image_to_string(image, lang='deu+eng+spa+fra+ita+pol+ces')
                except:
                    # Further fallback: Basic languages
                    try:
                        text = pytesseract.image_to_string(image, lang='deu+eng')
                    except:
                        # Last resort: No language specification
                        try:
                            text = pytesseract.image_to_string(image)
                        except:
                            return f"[Tesseract OCR not installed on system. Install tesseract-ocr package.]"

            if text.strip():
                return f"[Tesseract OCR]\n{text.strip()}"
            else:
                return "[Tesseract OCR: No text found in image]"
        except Exception as e:
            return f"[Tesseract OCR Error: {str(e)}]"

    def _parse_image_paddle(self, file_path: str) -> str:
        """Extract text from image using PaddleOCR"""
        if not PADDLE_AVAILABLE:
            return "[PaddleOCR not available - install paddleocr]"

        if not self.paddle_ocr:
            return "[PaddleOCR not initialized]"

        try:
            # PaddleOCR returns list of [bbox, (text, confidence)]
            result = self.paddle_ocr.ocr(file_path, cls=True)

            if not result or not result[0]:
                return "[PaddleOCR: No text found in image]"

            # Extract text from results
            text_lines = []
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # Extract text from (text, confidence) tuple
                    confidence = line[1][1]
                    text_lines.append(text)

            extracted_text = "\n".join(text_lines)

            if extracted_text.strip():
                return f"[PaddleOCR]\n{extracted_text.strip()}"
            else:
                return "[PaddleOCR: No text extracted]"

        except Exception as e:
            return f"[PaddleOCR Error: {str(e)}]"

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
