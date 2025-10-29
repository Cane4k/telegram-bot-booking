import logging
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters
)
from config import TELEGRAM_TOKEN, ADMIN_IDS
from handlers.user_handlers import *
from handlers.admin_handlers import *

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Запуск бота"""
    print("🤖 Запуск бота...")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Команда /start (должна быть первой!)
    application.add_handler(CommandHandler("start", start))
    
    # ConversationHandler для записи
    booking_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📝 Записаться$"), book_start)
        ],
        states={
            SELECTING_WHEEL: [
                CallbackQueryHandler(wheel_selected, pattern="^wheel_")
            ],
            ENTERING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, name_entered)
            ],
            SELECTING_DATE: [
                CallbackQueryHandler(date_selected, pattern="^date_")
            ],
            SELECTING_TIME: [
                CallbackQueryHandler(time_selected, pattern="^(time_|back_)")
            ],
            ENTERING_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, comment_entered),
                CallbackQueryHandler(comment_skipped, pattern="^skip_comment$")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command)
        ]
    )
    
    # ConversationHandler для отмены записи пользователем
    cancel_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^❌ Отменить запись$"), cancel_start)
        ],
        states={
            CANCEL_SELECTING: [
                CallbackQueryHandler(cancel_booking_selected, pattern="^(cancel_)")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command)
        ]
    )
    
    # ConversationHandler для удаления записи админом
    admin_delete_conv = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^🗑 Удалить запись$") & filters.User(ADMIN_IDS), 
                admin_delete_start
            )
        ],
        states={
            SELECTING_BOOKING_TO_DELETE: [
                CallbackQueryHandler(admin_delete_booking_selected, pattern="^(admin_delete_)")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_command)
        ]
    )
    
    # Добавляем ConversationHandlers
    application.add_handler(booking_conv)
    application.add_handler(cancel_conv)
    application.add_handler(admin_delete_conv)
    
    # Пользовательская кнопка "Мои записи"
    application.add_handler(
        MessageHandler(filters.Regex("^📋 Мои записи$"), my_bookings)
    )
    
    # Админские кнопки (только для администраторов)
    application.add_handler(
        MessageHandler(
            filters.Regex("^📅 Сегодня$") & filters.User(ADMIN_IDS), 
            admin_today_bookings
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Regex("^📆 Завтра$") & filters.User(ADMIN_IDS), 
            admin_tomorrow_bookings
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Regex("^📊 На неделю$") & filters.User(ADMIN_IDS), 
            admin_week_bookings
        )
    )
    application.add_handler(
        MessageHandler(
            filters.Regex("^👤 Режим пользователя$") & filters.User(ADMIN_IDS), 
            admin_to_user_mode
        )
    )
    
    # Запуск бота
    print("✅ Бот запущен и работает!")
    print("Нажмите Ctrl+C для остановки")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()