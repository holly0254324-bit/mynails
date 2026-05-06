from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

SERVICE_ACCOUNT_FILE = 'service_account.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

service = build('calendar', 'v3', credentials=credentials)

CALENDAR_ID = 'primary'

//ПОЛУЧЕНИЕ СОБІТИЙ//

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TIMEZONE = ZoneInfo("Europe/Vienna")


def get_events_for_day(date):
    start = datetime(date.year, date.month, date.day, 0, 0, tzinfo=TIMEZONE)
    end = start + timedelta(days=1)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    return events_result.get('items', [])

// +++++++Конвертация в busy slots ++++++//
def get_busy_slots(date):
    events = get_events_for_day(date)

    busy = []

    for event in events:
        start = datetime.fromisoformat(event['start']['dateTime'])
        end = datetime.fromisoformat(event['end']['dateTime'])

        busy.append((start, end))

    return busy
