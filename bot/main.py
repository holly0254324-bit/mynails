from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from datetime import datetime
from config import BOT_TOKEN, SERVICE_DURATIONS
from services.booking import get_available_slots
from services.calendar_service import get_busy_slots


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Маникюр", callback_data="manicure")],
        [InlineKeyboardButton("Педикюр", callback_data="pedicure")],
        [InlineKeyboardButton("Маникюр + Педикюр", callback_data="combo")],
    ]

    await update.message.reply_text(
        "Выберите услугу 💅",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service = query.data
    context.user_data["service"] = service

    today = datetime.now()

    slots = get_available_slots(
        today,
        SERVICE_DURATIONS[service],
        existing_events=[],  # сюда потом Google Calendar
    )

    if not slots:
        await query.edit_message_text("Сегодня уже всё занято 😢")
        return

    busy_slots = get_busy_slots(today)

    slots = get_available_slots(
        today,
        SERVICE_DURATIONS[service],
        existing_events=busy_slots
    )

    keyboard = [
        [InlineKeyboardButton(slot, callback_data=f"time_{slot}")]
        for slot in slots[:10]  # ограничим, чтобы не взорвать интерфейс
    ]

    await query.edit_message_text(
        "Выберите время:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    time = query.data.replace("time_", "")
    service = context.user_data.get("service")

    await query.edit_message_text(
        f"Запись подтверждена 💅\n\nУслуга: {service}\nВремя: {time}"
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(select_service, pattern="^(manicure|pedicure|combo)$"))
    app.add_handler(CallbackQueryHandler(select_time, pattern="^time_"))

    app.run_polling()

def create_event(start_time, duration_minutes, user_name, service_name):
    end_time = start_time + timedelta(minutes=duration_minutes)

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
        body=event
    ).execute()

    return created_event

if __name__ == "__main__":
    main()
