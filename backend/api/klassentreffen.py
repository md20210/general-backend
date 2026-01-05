"""Klassentreffen API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from backend.database import get_async_session
from backend.models.klassentreffen import Participant

router = APIRouter(prefix="/api/klassentreffen", tags=["klassentreffen"])


class EmailRegistration(BaseModel):
    """Email registration model."""
    name: str
    email: EmailStr
    consent: bool = True


class ParticipantResponse(BaseModel):
    """Participant response model."""
    name: str
    email: Optional[str] = None
    consent: Optional[bool] = False
    registered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CountResponse(BaseModel):
    """Count response model."""
    count: int


@router.post("/register")
async def register_email(
    registration: EmailRegistration,
    session: AsyncSession = Depends(get_async_session)
):
    """Register or update email address for a participant."""
    # Update participant email and consent
    stmt = (
        update(Participant)
        .where(Participant.name == registration.name)
        .values(
            email=registration.email,
            consent=registration.consent,
            registered_at=datetime.utcnow()
        )
        .returning(Participant)
    )

    result = await session.execute(stmt)
    await session.commit()
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Name nicht gefunden")

    return {
        "success": True,
        "message": "E-Mail erfolgreich registriert!",
        "name": participant.name,
        "email": participant.email
    }


@router.get("/count", response_model=CountResponse)
async def get_count(session: AsyncSession = Depends(get_async_session)):
    """Get count of registered participants."""
    stmt = select(Participant).where(Participant.email.isnot(None))
    result = await session.execute(stmt)
    participants = result.scalars().all()

    return CountResponse(count=len(participants))


@router.get("/participants", response_model=List[ParticipantResponse])
async def get_participants(session: AsyncSession = Depends(get_async_session)):
    """Get all participants."""
    stmt = select(Participant).order_by(Participant.name)
    result = await session.execute(stmt)
    participants = result.scalars().all()

    return [ParticipantResponse.from_orm(p) for p in participants]


@router.get("/registered", response_model=List[ParticipantResponse])
async def get_registered(session: AsyncSession = Depends(get_async_session)):
    """Get only registered participants (with email)."""
    stmt = (
        select(Participant)
        .where(Participant.email.isnot(None))
        .order_by(Participant.registered_at.desc())
    )
    result = await session.execute(stmt)
    participants = result.scalars().all()

    return [ParticipantResponse.from_orm(p) for p in participants]
