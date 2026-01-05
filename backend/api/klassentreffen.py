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


@router.delete("/admin/delete/{name}")
async def delete_participant_email(
    name: str,
    session: AsyncSession = Depends(get_async_session)
):
    """Admin endpoint to delete a participant's email (reset to null)."""
    # Update participant to remove email and consent
    stmt = (
        update(Participant)
        .where(Participant.name == name)
        .values(email=None, consent=False, registered_at=None)
        .returning(Participant)
    )

    result = await session.execute(stmt)
    await session.commit()
    participant = result.scalar_one_or_none()

    if not participant:
        raise HTTPException(status_code=404, detail="Name nicht gefunden")

    return {
        "success": True,
        "message": "E-Mail-Adresse gelöscht",
        "name": participant.name
    }


@router.post("/admin/populate")
async def populate_participants(session: AsyncSession = Depends(get_async_session)):
    """Admin endpoint to populate participants (one-time use)."""
    # Check if already populated
    stmt = select(Participant)
    result = await session.execute(stmt)
    existing = result.scalars().all()

    if len(existing) > 0:
        return {"message": f"Already populated with {len(existing)} participants"}

    # All 133 names
    names = [
        "Carsten Dobschall", "Michael Dütting", "Ansgar Ellermann", "Irene Etmann (jetzt: Bils)",
        "Klaus Gunnemann", "Stefan Hille", "Peter Hoppe", "Martina Höptner (jetzt: Hecker)",
        "Stephan Horstmann", "Ralf Huihsen", "Stephan Kappen", "Klaus Klöker",
        "Bernd Kottmann", "Klaus Loskant", "Sabine Lünnemann (jetzt: Vortkamp)", "Andreas Menke",
        "Stephan Quiel", "Roland Rietkoetter", "Olaf Saphörster", "Annette Schwarte",
        "Andre Sickmann", "Thomas Siebert", "Eike Silvester Wiemann", "Magnus Wolke",
        "Heinz Wöstmann", "Gernot Becker", "Christiane Buck (jetzt: Schmidt)", "Michael Dabrock",
        "Jochen Dahm", "Melanie Dörholt", "Birgit Dohmen (jetzt: Decker)", "Patric Droste zu Senden",
        "Roman Feil", "Georg Fels", "Andreas Golf", "Klaus Günther",
        "Volker Hahn", "Karin Harnisch", "Frank Kloppenburg", "Dirk Köwener",
        "Harald Kröger", "Peter Lahrkamp", "Bernd Lehmann", "Katrin Lumma",
        "Mechthild Lütke Kleimann", "Silke Mersmann (jetzt: Born)", "Dirk Neufelder", "Ursula Neumann",
        "Josef Niehoff", "Stefan Niggemeyer", "Gerhard Nowak", "Madueke Okegwo",
        "Renate Ostermeyer", "Bettina Otto", "Mechthild Rickert", "Axel Ritter",
        "Eva Sandhage (jetzt: Wehmeyer-Sandhage)", "Ralf Schupp", "Bettina Seidensticker", "Martin Sommermeyer",
        "Peter Sperling", "Wolfgang Spille", "Benedikt Sudbrock", "Thomas Terrahe",
        "Volker Welp", "Susanne Wettwer", "Uwe Wilme", "Reinhold Albrecht",
        "Peter Alt-Epping", "Konstanze Bader", "Michael Beneke", "Marc Böddecker",
        "Georg Bratke", "Carsten Brüning", "Andreas Döpp", "Jürgen Dorgeist",
        "Oliver Dütschke", "Dirk Eberhardt", "Reinhild Erling", "Marie-Luise Ernst (jetzt: Terrahe)",
        "Mathias Eßing", "Karsten Evers", "Christian Fischer", "Sabine Gädeke",
        "Veronica Gohl", "Anne Grewe (jetzt: Vetter)", "Monika Haye (jetzt: Gaedeke)", "Jörg Hecker",
        "Andrea Heller", "Ingo Hentschel", "Jörg Hesselink", "Annegret Hobbeling",
        "Markus Hock", "Thomas Hörnemann", "Bettina Horstmann", "Volker Hund",
        "Marcus Janotta", "Stephan Kehr", "Renate Kellers (jetzt:? Herzog)", "Martin Kintrup",
        "Annette Knirim", "Bernd Korves", "Michael Laermann", "Petra Lindner (jetzt: Hubeny-Lindner)",
        "Dominik Löer", "Friedrich Lührmann", "Arno Lutz", "David Lützenkirchen",
        "Henning Meißner", "Frank Mense", "Thomas Mertens", "Matthias Michalczyk",
        "Oliver Müllmann", "Anja Neumann-Wedekindt", "Jürgen Proch", "David Rehmann",
        "Katrin Richter", "Barbara Sauer", "Fabian Sauerwald", "Tobias Sauerwald",
        "Klaus Schaphorn", "Thomas Schleicher", "Anne Schlummer", "Frank Schulte",
        "Ludger Schwarte", "Harald Siegmund", "Andreas Südbeck", "Helmut Südmersen",
        "Wolfgang Thomas", "Clarus von der Horst", "Kai Wengler", "Melanie Wessels",
        "Roland Wilmes"
    ]

    # Insert all participants
    for name in names:
        participant = Participant(name=name, consent=False)
        session.add(participant)

    await session.commit()

    return {"message": f"Successfully populated {len(names)} participants"}
