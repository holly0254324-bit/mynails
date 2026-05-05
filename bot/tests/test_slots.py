from datetime import datetime, timedelta
from services.booking import get_available_slots


def test_future_date():
    date = datetime.now() + timedelta(days=1)
    slots = get_available_slots(date, 90)
    assert len(slots) > 0


def test_past_date():
    date = datetime.now() - timedelta(days=1)
    slots = get_available_slots(date, 90)
    assert slots == []


def test_today_buffer():
    now = datetime.now()
    slots = get_available_slots(now, 90)

    # проверяем, что ближайший слот >= 1 часа
    first_slot = datetime.strptime(slots[0], "%H:%M")
    assert first_slot.minute in (0, 30)
