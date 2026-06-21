"""
Google Calendar API Routes
Endpoints for calendar booking and availability
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
import os

from backend.services.calendar.google_calendar import calendar_service


router = APIRouter(prefix="/calendar", tags=["calendar"])


class CreateEventRequest(BaseModel):
    """Request model for creating a calendar event"""
    name: str
    email: EmailStr
    message: Optional[str] = ""
    start: str  # ISO datetime string
    end: str    # ISO datetime string


class AvailableSlotsRequest(BaseModel):
    """Request model for getting available slots"""
    start: str  # ISO datetime string
    end: str    # ISO datetime string


@router.post("/create-event")
async def create_calendar_event(request: CreateEventRequest):
    """
    Create a new calendar event with Google Meet link

    Creates an event in michael.dabrock@gmail.com calendar
    and sends invitations to both parties.
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(request.start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(request.end.replace('Z', '+00:00'))

        # Create event
        event = calendar_service.create_event(
            summary=f"Consultation: {request.name}",
            description=f"""
**Client Details:**
- Name: {request.name}
- Email: {request.email}

**Message:**
{request.message or 'No message provided'}

---
Booked via dabrock.ai
            """.strip(),
            start=start_dt,
            end=end_dt,
            attendees=[
                request.email,
                os.getenv('GOOGLE_CALENDAR_EMAIL', 'michael.dabrock@gmail.com')
            ]
        )

        return {
            "success": True,
            "event": event
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-slots")
async def get_available_slots(start: str, end: str):
    """
    Get available 30-minute time slots

    Returns slots between start and end time that are not blocked
    in the calendar. Only returns slots during business hours (9-18).
    """
    try:
        # Parse datetime strings
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

        # Get available slots
        slots = calendar_service.get_available_slots(
            time_min=start_dt,
            time_max=end_dt,
            slot_duration_minutes=30
        )

        return {
            "slots": slots,
            "count": len(slots)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def calendar_health_check():
    """Health check for calendar service"""
    has_credentials = all([
        os.getenv('GOOGLE_CLIENT_ID'),
        os.getenv('GOOGLE_CLIENT_SECRET'),
        os.getenv('GOOGLE_REFRESH_TOKEN'),
    ])

    return {
        "status": "healthy" if has_credentials else "missing_credentials",
        "credentials_configured": has_credentials
    }
