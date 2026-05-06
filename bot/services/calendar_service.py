import os

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
):
    end_time = start_time + timedelta(
        minutes=duration_minutes
    )

    event = {
        'summary': f'{service_name} - {user_name}',
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
