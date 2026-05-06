from datetime import datetime
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
        f"Запись подтверждена 💅\n\n"
        f"Услуга: {service}\n"
        f"Время: {time_str}"
    )


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
