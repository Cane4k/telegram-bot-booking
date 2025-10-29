from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_main_keyboard, get_delete_booking_keyboard
from database import (
    get_today_bookings, 
    get_tomorrow_bookings, 
    get_week_bookings,
    get_all_active_bookings,
    admin_delete_booking
)

# Состояние для диалога удаления
SELECTING_BOOKING_TO_DELETE = 1

async def admin_today_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать записи на сегодня"""
    bookings = get_today_bookings()
    
    if not bookings:
        await update.message.reply_text("📭 На сегодня записей нет.")
        return
    
    text = f"📅 Записи на сегодня ({len(bookings)}):\n\n"
    
    for i, booking in enumerate(bookings, 1):
        text += (
            f"{i}. ⏰ {booking['Время']} — {booking.get('Имя клиента', 'N/A')}\n"
            f"   🛞 {booking['Размер колес']}\n\n"
        )
    
    await update.message.reply_text(text)

async def admin_tomorrow_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать записи на завтра"""
    bookings = get_tomorrow_bookings()
    
    if not bookings:
        await update.message.reply_text("📭 На завтра записей нет.")
        return
    
    text = f"📆 Записи на завтра ({len(bookings)}):\n\n"
    
    for i, booking in enumerate(bookings, 1):
        text += (
            f"{i}. ⏰ {booking['Время']} — {booking.get('Имя клиента', 'N/A')}\n"
            f"   🛞 {booking['Размер колес']}\n\n"
        )
    
    await update.message.reply_text(text)

async def admin_week_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать записи на неделю"""
    bookings = get_week_bookings()
    
    if not bookings:
        await update.message.reply_text("📭 На эту неделю записей нет.")
        return
    
    text = f"📊 Записи на неделю ({len(bookings)}):\n\n"
    
    current_date = None
    for i, booking in enumerate(bookings, 1):
        # Группируем по датам
        if current_date != booking['Дата']:
            current_date = booking['Дата']
            text += f"\n📅 {current_date}:\n"
        
        text += (
            f"{i}. ⏰ {booking['Время']} — {booking.get('Имя клиента', 'N/A')} "
            f"({booking['Размер колес']})\n"
        )
    
    await update.message.reply_text(text)

async def admin_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса удаления записи"""
    bookings = get_all_active_bookings()
    
    if not bookings:
        await update.message.reply_text("📭 Активных записей нет.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"🗑 Выберите запись для удаления ({len(bookings)} записей):",
        reply_markup=get_delete_booking_keyboard(bookings)
    )
    return SELECTING_BOOKING_TO_DELETE

async def admin_delete_booking_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка удаления выбранной записи"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_delete_back":
        await query.edit_message_text("❌ Удаление отменено.")
        return ConversationHandler.END
    
    # Парсим дату и время из callback_data
    parts = query.data.replace("admin_delete_", "").split("_")
    date = parts[0]  # ДД
    month = parts[1]  # ММ
    year = parts[2]   # ГГГГ
    time = parts[3] + ":" + parts[4]  # ЧЧ:ММ
    
    full_date = f"{date}.{month}.{year}"
    
    print(f"[DEBUG] Парсинг: date={full_date}, time={time}")
    
    success = admin_delete_booking(full_date, time)
    
    if success:
        await query.edit_message_text(
            f"✅ Запись на {full_date} в {time} успешно удалена."
        )
    else:
        await query.edit_message_text(
            "❌ Ошибка при удалении записи. Попробуйте позже."
        )
    
    return ConversationHandler.END

async def admin_to_user_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключение в режим пользователя"""
    await update.message.reply_text(
        "👤 Переключено в пользовательский режим.",
        reply_markup=get_main_keyboard()
    )