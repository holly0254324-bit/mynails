from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.config import BOT_TOKEN, SERVICE_DURATIONS
from bot.services.booking import get_available_slots
from bot.services.calendar_service import (
    get_busy_slots,
    create_event,
)

TIMEZONE = ZoneInfo("Europe/Vienna")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Манікюр", callback_data="manicure")],
        [InlineKeyboardButton("Педикюр", callback_data="pedicure")],
        [InlineKeyboardButton("Манікюр + Педикюр", callback_data="manicure_pedicure")],
    ]

    await update.message.reply_text(
        f"Вітаю 🌸\n"
        f"Я віртуальний помічник 👩‍🦰 і допоможу швидко записатися до майстра 💅\n\n"

        f"Доступні послуги:\n"
        f" • Манікюр - 600 грн. (1,5 години)\n"
        f" • Педикюр - 800 грн. без п'яток (2 години)\n"
        f" • Манікюр + педикюр - 1200 грн. (3 години)\n"
        f" • Дизайн нігтів – від 100 грн.\n\n"

        f"Виберіть послугу нижче, і я підберу вам зручний час ✨",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service = query.data
    context.user_data["service"] = service

    today = datetime.now(TIMEZONE).date()

    keyboard = []

    for i in range(14):
        date = today + timedelta(days=i)

        formatted_date = date.strftime("%d.%m")

        if i == 0:
            text = f"Сьогодні ({formatted_date})"
        elif i == 1:
            text = f"Завтра ({formatted_date})"
        else:
            text = formatted_date

        keyboard.append([
            InlineKeyboardButton(
                text,
                callback_data=f"date_{date.isoformat()}"
            )
        ])

    await query.edit_message_text(
        "📅 Оберіть дату:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    date_str = query.data.replace("date_", "")

    selected_date = datetime.fromisoformat(date_str)

    context.user_data["selected_date"] = selected_date

    service = context.user_data.get("service")

    busy_slots = get_busy_slots(selected_date)

    slots = get_available_slots(
        selected_date,
        SERVICE_DURATIONS[service],
        existing_events=busy_slots,
    )

    if not slots:
        await query.edit_message_text(
            "😢 На цю дату вільних слотів немає"
        )
        return

    keyboard = [
        [InlineKeyboardButton(slot, callback_data=f"time_{slot}")]
        for slot in slots
    ]

    await query.edit_message_text(
        f"⏰ Оберіть час на {selected_date.strftime('%d.%m.%Y')}:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    time_str = query.data.replace("time_", "")
    service = context.user_data.get("service")

    selected_date = context.user_data.get("selected_date")

    context.user_data["selected_time"] = time_str

    keyboard = [
        [
            KeyboardButton(
                text="📱 Поділитися номером",
                request_contact=True,
            )
        ]
    ]

    await query.message.reply_text(
        "📱 Будь ласка, поділіться номером телефону:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True,
        ),
    )


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact

    phone_number = contact.phone_number

    context.user_data["phone_number"] = phone_number

    service = context.user_data.get("service")

    duration = SERVICE_DURATIONS[service]

    selected_date = context.user_data.get("selected_date")

    time_str = context.user_data.get("selected_time")

    hour, minute = map(int, time_str.split(":"))

    start_time = datetime(
        selected_date.year,
        selected_date.month,
        selected_date.day,
        hour,
        minute,
        tzinfo=TIMEZONE,
    )

    create_event(
        start_time=start_time,
        duration_minutes=duration,
        user_name=update.effective_user.first_name,
        service_name=service,
        phone_number=phone_number,
    )

    await update.message.reply_text(
        f"✅ ЗАПИС ПІДТВЕРДЖЕНО! 💅\n\n"

        f"📍 Чекаю на вас за адресою:\n"
        f"м. Київ, вул. Хрещатик, 116a\n\n"

        f"📌 Послуга: {service}\n"
        f"⏰ Час: {time_str}\n"
        f"🗓 Дата: {start_time.strftime('%d.%m.%Y')}\n"
        f"📱 Телефон: {phone_number}\n\n"

        f"✔️ Якщо потрібно змінити час або послугу — просто напишіть мені знову.\n\n"

        f"✔️ Якщо потрібно скасувати або перенести запис — будь ласка, повідомте заздалегідь.\n\n"

        f"До зустрічі 🌸",

        reply_markup=ReplyKeyboardRemove(),
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            select_service,
            pattern="^(manicure|pedicure|manicure_pedicure)$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_date,
            pattern="^date_",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_time,
            pattern="^time_",
        )
    )

    app.add_handler(
        MessageHandler(
            filters.CONTACT,
            handle_contact,
        )
    )

    print("BOT STARTED")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

