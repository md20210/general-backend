"""
Google Calendar Service
Handles all Google Calendar API interactions
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarService:
    """Service for Google Calendar API operations"""

    def __init__(self):
        """Initialize with credentials from environment"""
        self.credentials = Credentials(
            token=os.getenv('GOOGLE_ACCESS_TOKEN'),
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=[
                'https://www.googleapis.com/auth/calendar.readonly',
                'https://www.googleapis.com/auth/calendar.events'
            ]
        )

    def get_service(self):
        """Get Google Calendar API service"""
        return build('calendar', 'v3', credentials=self.credentials)

    def create_event(
        self,
        summary: str,
        description: str,
        start: datetime,
        end: datetime,
        attendees: List[str],
        calendar_id: str = 'primary'
    ) -> Dict:
        """
        Create a calendar event with Google Meet link

        Args:
            summary: Event title
            description: Event description
            start: Start datetime
            end: End datetime
            attendees: List of attendee emails
            calendar_id: Calendar ID (default: 'primary')

        Returns:
            Dict with event details including Google Meet link
        """
        try:
            service = self.get_service()

            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'end': {
                    'dateTime': end.isoformat(),
                    'timeZone': 'Europe/Madrid',
                },
                'attendees': [{'email': email} for email in attendees],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"{int(datetime.now().timestamp())}"
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},  # 30 minutes before
                    ],
                },
            }

            created_event = service.events().insert(
                calendarId=calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            return {
                'id': created_event.get('id'),
                'htmlLink': created_event.get('htmlLink'),
                'hangoutLink': created_event.get('hangoutLink'),
                'start': created_event.get('start'),
                'end': created_event.get('end'),
            }

        except HttpError as error:
            raise Exception(f'Google Calendar API error: {error}')

    def get_freebusy(
        self,
        time_min: datetime,
        time_max: datetime,
        calendar_id: str = 'primary'
    ) -> List[Dict]:
        """
        Get busy time slots

        Args:
            time_min: Start time
            time_max: End time
            calendar_id: Calendar ID

        Returns:
            List of busy time periods
        """
        try:
            service = self.get_service()

            body = {
                'timeMin': time_min.isoformat() + 'Z',
                'timeMax': time_max.isoformat() + 'Z',
                'items': [{'id': calendar_id}]
            }

            events_result = service.freebusy().query(body=body).execute()
            busy_slots = events_result['calendars'][calendar_id].get('busy', [])

            return busy_slots

        except HttpError as error:
            raise Exception(f'Google Calendar API error: {error}')

    def get_available_slots(
        self,
        time_min: datetime,
        time_max: datetime,
        slot_duration_minutes: int = 30,
        calendar_id: str = 'primary'
    ) -> List[Dict]:
        """
        Calculate available time slots

        Args:
            time_min: Start time
            time_max: End time
            slot_duration_minutes: Duration of each slot
            calendar_id: Calendar ID

        Returns:
            List of available slots with start and end times
        """
        busy_slots = self.get_freebusy(time_min, time_max, calendar_id)

        available_slots = []
        current_time = time_min
        slot_duration = timedelta(minutes=slot_duration_minutes)

        while current_time < time_max:
            slot_end = current_time + slot_duration

            # Check if slot overlaps with any busy period
            is_available = True
            for busy in busy_slots:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))

                # Check for overlap
                if current_time < busy_end and slot_end > busy_start:
                    is_available = False
                    break

            # Only include slots during business hours (9-18)
            hour = current_time.hour
            if is_available and 9 <= hour < 18:
                available_slots.append({
                    'start': current_time.isoformat(),
                    'end': slot_end.isoformat()
                })

            current_time = slot_end

        return available_slots


# Singleton instance
calendar_service = GoogleCalendarService()
