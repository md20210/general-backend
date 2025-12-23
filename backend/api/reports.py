"""Reports API endpoints for PDF generation."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.auth.dependencies import current_active_user
from backend.database import get_async_session
from backend.models.user import User
from backend.services.pdf_service import pdf_service


router = APIRouter(prefix="/reports", tags=["reports"])


class ChatMessage(BaseModel):
    """Chat message for PDF generation."""
    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp (ISO format)")


class ComparisonItem(BaseModel):
    """Comparison item for detailed table."""
    requirement: str
    applicant_match: str
    details: Optional[str] = None
    match_level: str = Field(..., description="full, partial, or missing")
    confidence: int = Field(..., ge=0, le=100)


class GeneratePDFRequest(BaseModel):
    """Request to generate PDF report."""
    match_result: dict = Field(..., description="Match analysis result from LLM")
    chat_history: Optional[List[ChatMessage]] = Field(default=None, description="Chat conversation history")


@router.post("/generate")
async def generate_pdf_report(
    request: GeneratePDFRequest,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    """
    Generate PDF report for CV match analysis.

    Includes:
    - Overall match score with visual indicator
    - Strengths and gaps in 2-column layout
    - Recommendations (if available)
    - Detailed comparison table (if available)
    - Detailed analysis text
    - Chat conversation history (if available)

    Returns PDF file as streaming response.
    """
    try:
        # Convert chat history to dict format expected by PDF service
        chat_history_dicts = None
        if request.chat_history:
            chat_history_dicts = [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in request.chat_history
            ]

        # Generate PDF
        pdf_buffer = pdf_service.generate_match_report(
            match_result=request.match_result,
            chat_history=chat_history_dicts
        )

        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=cv_match_report.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )
