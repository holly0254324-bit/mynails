from datetime import datetime
from zoneinfo import ZoneInfo

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
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
        [InlineKeyboardButton("Маникюр", callback_data="manicure")],
        [InlineKeyboardButton("Педикюр", callback_data="pedicure")],
        [InlineKeyboardButton("Маникюр + Педикюр", callback_data="combo")],
    ]

    await update.message.reply_text(
        f"Вітаю 🌸\n"
        f"Я віртуальний помічник 👩‍🦰 і допоможу швидко записатися до майстра 💅\n"
        f"Доступні послуги:\n"
        f" • Манікюр - 600 грн. (1,5 години)\n"
        f" • Педикюр - 800 грн. без п'яток (2 години)\n"
        f" • Манікюр + педикюр - 1200 грн. (3 години)\n"
        f" • Дизайн нігтів – від 100 грн.\n"
        f" • Виберіть послугу нижче, і я підберу вам зручний час ✨\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
        

async def select_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service = query.data
    context.user_data["service"] = service

    today = datetime.now(TIMEZONE)

    busy_slots = get_busy_slots(today)

    slots = get_available_slots(
        today,
        SERVICE_DURATIONS[service],
        existing_events=busy_slots,
    )

    if not slots:
        await query.edit_message_text(
            "Сьогодні вільних слотів немає 😢"
        )
        return

    keyboard = [
        [InlineKeyboardButton(slot, callback_data=f"time_{slot}")]
        for slot in slots
    ]

    await query.edit_message_text(
        "Виберіть час:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def select_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    time_str = query.data.replace("time_", "")
    service = context.user_data.get("service")

    duration = SERVICE_DURATIONS[service]

    now = datetime.now(TIMEZONE)

    hour, minute = map(int, time_str.split(":"))

    start_time = datetime(
        now.year,
        now.month,
        now.day,
        hour,
        minute,
        tzinfo=TIMEZONE,
    )

    create_event(
        start_time=start_time,
        duration_minutes=duration,
        user_name=query.from_user.first_name,
        service_name=service,
    )

    await query.edit_message_text(
        f"Запис підтверджений! 💅 Чекаю на вас за адресою: м. Київ, вул. Хрещатик, 116a\n\n"
        f"Послуга: {service}\n"
        f"Час: {time_str}\n" 
        f"Дата: {start_time.strftime('%d.%m.%Y')}\n\n"
        f"Якщо потрібно змінити час або послугу, просто напишіть мені знову.\n\n"
       
        f"Якщо потрібно скасувати або перенести запис, будь ласка, зв'яжіться зі мною заздалегідь.\n"

        f"Якщо у вас є питання або потрібна допомога, не соромтеся звертатися до мене в будь-який час. Я завжди готова допомогти вам з вашими записами та надати інформацію про послуги.\n"
      
        f"До зустрічі! 🌸")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(
            select_service,
            pattern="^(manicure|pedicure|combo)$",
        )
    )

    app.add_handler(
        CallbackQueryHandler(
            select_time,
            pattern="^time_",
        )
    )

    print("BOT STARTED")

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
