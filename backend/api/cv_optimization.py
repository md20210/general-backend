"""CV Optimization API endpoints - Public file extraction service."""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
import os
import shutil
import tempfile

from backend.services.document_processor import document_processor


router = APIRouter(prefix="/cv-optimization", tags=["cv-optimization"])


@router.post("/extract-text")
async def extract_cv_text(
    file: UploadFile = File(...),
):
    """
    Extract text from uploaded CV file (PDF, DOCX, or TXT).

    This is a public endpoint (no authentication required) designed for
    CV Optimization frontend to extract text from uploaded CVs.

    Args:
        file: Uploaded file (PDF, DOCX, or TXT)

    Returns:
        JSON with extracted text and metadata
    """
    # Validate file type
    filename = file.filename.lower() if file.filename else ""

    if filename.endswith('.pdf'):
        file_type = 'pdf'
    elif filename.endswith('.docx'):
        file_type = 'docx'
    elif filename.endswith('.txt'):
        file_type = 'txt'
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, and TXT files are supported"
        )

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
        temp_path = temp_file.name

        try:
            # Save uploaded file to temp location
            shutil.copyfileobj(file.file, temp_file)
            temp_file.flush()

            # Extract text based on file type
            if file_type == 'txt':
                # Plain text file - read directly
                with open(temp_path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
            elif file_type == 'pdf':
                # PDF file
                with open(temp_path, "rb") as f:
                    content = document_processor.extract_from_pdf(f)
            elif file_type == 'docx':
                # DOCX file
                with open(temp_path, "rb") as f:
                    content = document_processor.extract_from_docx(f)
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Unsupported file type: {file_type}"
                )

            # Get file size
            file_size = os.path.getsize(temp_path)

            return JSONResponse(content={
                "success": True,
                "filename": file.filename,
                "file_type": file_type,
                "file_size": file_size,
                "text": content,
                "text_length": len(content),
                "word_count": len(content.split())
            })

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to extract text: {str(e)}"
            )

        finally:
            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)


@router.get("/health")
async def health_check():
    """Health check endpoint for CV Optimization service."""
    return {
        "status": "healthy",
        "service": "cv-optimization",
        "supported_formats": ["pdf", "docx", "txt"]
    }
