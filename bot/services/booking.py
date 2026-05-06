from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bot.config import (
    WORK_START,
    WORK_END,
    SLOT_STEP_MINUTES,
)

TIMEZONE = ZoneInfo("Europe/Vienna")


def generate_time_slots(date):
    start = datetime(
        date.year,
        date.month,
        date.day,
        WORK_START,
        0,
        tzinfo=TIMEZONE,
    )

    end = datetime(
        date.year,
        date.month,
        date.day,
        WORK_END,
        0,
        tzinfo=TIMEZONE,
    )

    slots = []
    current = start

    while current < end:
        slots.append(current)
        current += timedelta(minutes=SLOT_STEP_MINUTES)

    return slots


def is_today(date):
    now = datetime.now(TIMEZONE)
    return date.date() == now.date()


def filter_past_and_buffer(slots):
    now = datetime.now(TIMEZONE)

    valid = []

    for slot in slots:
        if slot <= now:
            continue

        if is_today(slot):
            if (slot - now) < timedelta(hours=1):
                continue

        valid.append(slot)

    return valid


def fits_working_hours(slot, duration_minutes):
    end_time = slot + timedelta(minutes=duration_minutes)

    return end_time.hour < WORK_END or (
        end_time.hour == WORK_END and end_time.minute == 0
    )


def overlaps(slot, duration_minutes, existing):
    slot_end = slot + timedelta(minutes=duration_minutes)

    for event_start, event_end in existing:
        if slot < event_end and slot_end > event_start:
            return True

    return False


def get_available_slots(date, duration_minutes, existing_events=None):
    if existing_events is None:
        existing_events = []

    now = datetime.now(TIMEZONE)

    if date.date() < now.date():
        return []

    slots = generate_time_slots(date)
    slots = filter_past_and_buffer(slots)

    valid_slots = []

    for slot in slots:
        if not fits_working_hours(slot, duration_minutes):
            continue

        if overlaps(slot, duration_minutes, existing_events):
            continue

        valid_slots.append(slot.strftime("%H:%M"))

    return valid_slots
