import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

SERVICE_ACCOUNT_FILE = '/etc/secrets/service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES,
)

service = build('calendar', 'v3', credentials=credentials)

CALENDAR_ID = os.getenv("CALENDAR_ID")

TIMEZONE = ZoneInfo("Europe/Vienna")


def get_events_for_day(date):
    start = datetime(
        date.year,
        date.month,
        date.day,
        0,
        0,
        tzinfo=TIMEZONE,
    )

    end = start + timedelta(days=1)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy='startTime',
    ).execute()

    return events_result.get('items', [])


def get_busy_slots(date):
    events = get_events_for_day(date)

    busy = []

    for event in events:
        if 'dateTime' not in event['start']:
            continue

        start = datetime.fromisoformat(
            event['start']['dateTime']
        )

        end = datetime.fromisoformat(
            event['end']['dateTime']
        )

        busy.append((start, end))

    return busy



def create_event(
    start_time,
    duration_minutes,
    user_name,
    service_name,
    phone_number=None,
):
    end_time = start_time + timedelta(
        minutes=duration_minutes
    )

    description = (
        f"Клієнт: {user_name}\n"
        f"Телефон: {phone_number}"
    )

    event = {
        'summary': f'{service_name} - {user_name}',
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Vienna',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Vienna',
        },
    }

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
    ).execute()

    return created_event


    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
    ).execute()

    return created_event

def delete_event(event_id):
    service.events().delete(
        calendarId=CALENDAR_ID,
        eventId=event_id,
    ).execute()
