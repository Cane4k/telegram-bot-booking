from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import *
from database import *
from config import ADMIN_IDS

# Состояния диалога
SELECTING_WHEEL, ENTERING_NAME, SELECTING_DATE, SELECTING_TIME, ENTERING_COMMENT = range(5)
CANCEL_SELECTING = range(1)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    
    if user_id in ADMIN_IDS:
        await update.message.reply_text(
            "👋 Добро пожаловать, администратор!\n\n"
            "Выберите режим работы:",
            reply_markup=get_admin_keyboard()
        )
    else:
        await update.message.reply_text(
            "👋 Добро пожаловать в систему записи!\n\n"
            "Нажмите 'Записаться', чтобы забронировать время.",
            reply_markup=get_main_keyboard()
        )

async def book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса записи"""
    await update.message.reply_text(
        "🛞 Выберите размер колёс:",
        reply_markup=get_wheel_size_keyboard()
    )
    return SELECTING_WHEEL

async def wheel_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора размера колёс"""
    query = update.callback_query
    await query.answer()
    
    wheel_size = query.data.replace("wheel_", "")
    context.user_data['wheel_size'] = wheel_size
    
    await query.edit_message_text(
        f"✅ Выбран размер: R{wheel_size}\n\n"
        "👤 Теперь введите ваше имя:"
    )
    return ENTERING_NAME

async def name_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода имени"""
    client_name = update.message.text.strip()
    
    if len(client_name) < 2:
        await update.message.reply_text(
            "❌ Имя слишком короткое. Пожалуйста, введите корректное имя:"
        )
        return ENTERING_NAME
    
    context.user_data['client_name'] = client_name
    
    await update.message.reply_text(
        f"✅ Имя: {client_name}\n\n"
        "📅 Теперь выберите дату:",
        reply_markup=get_date_keyboard()
    )
    return SELECTING_DATE

async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора даты"""
    query = update.callback_query
    await query.answer()
    
    date = query.data.replace("date_", "")
    context.user_data['date'] = date
    
    booked_times = get_booked_times(date)
    
    await query.edit_message_text(
        f"📅 Дата: {date}\n\n"
        "⏰ Выберите удобное время:",
        reply_markup=get_time_keyboard(booked_times)
    )
    return SELECTING_TIME

async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора времени"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "back_to_wheels":
        await query.edit_message_text(
            "🛞 Выберите размер колёс:",
            reply_markup=get_wheel_size_keyboard()
        )
        return SELECTING_WHEEL
    
    time = query.data.replace("time_", "")
    context.user_data['time'] = time
    
    await query.edit_message_text(
        f"⏰ Время: {time}\n\n"
        "💬 Добавьте комментарий (опционально):\n"
        "(например: 'Приеду с дополнительными колёсами')"
        "\n\nИли нажмите кнопку 'Пропустить':",
        reply_markup=get_skip_comment_keyboard()
    )
    return ENTERING_COMMENT

async def comment_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода комментария"""
    comment = update.message.text.strip()
    
    if len(comment) > 200:
        await update.message.reply_text(
            "❌ Комментарий слишком длинный (максимум 200 символов). Пожалуйста, укоротите:"
        )
        return ENTERING_COMMENT
    
    await save_and_confirm(update, context, comment)
    return ConversationHandler.END

async def comment_skipped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Пропуск комментария"""
    query = update.callback_query
    await query.answer()
    
    await query.delete_message()
    await save_and_confirm_via_context(update, context, "")
    return ConversationHandler.END

async def save_and_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, comment: str):
    """Сохранение записи и подтверждение"""
    user = update.effective_user
    
    success = save_booking(
        user.id,
        user.username or user.first_name,
        context.user_data['client_name'],
        context.user_data['wheel_size'],
        context.user_data['date'],
        context.user_data['time'],
        comment
    )
    
    if success:
        await update.message.reply_text(
            f"✅ Запись успешно создана!\n\n"
            f"👤 Имя: {context.user_data['client_name']}\n"
            f"🛞 Размер колёс: R{context.user_data['wheel_size']}\n"
            f"📅 Дата: {context.user_data['date']}\n"
            f"⏰ Время: {context.user_data['time']}\n"
            f"💬 Комментарий: {comment or '(не добавлен)'}\n\n"
            f"Ждём вас!"
        )
    else:
        await update.message.reply_text(
            "❌ Ошибка при создании записи. Попробуйте позже."
        )
    
    context.user_data.clear()

async def save_and_confirm_via_context(update: Update, context: ContextTypes.DEFAULT_TYPE, comment: str):
    """Сохранение записи через callback (для пропуска)"""
    user = update.effective_user
    
    success = save_booking(
        user.id,
        user.username or user.first_name,
        context.user_data['client_name'],
        context.user_data['wheel_size'],
        context.user_data['date'],
        context.user_data['time'],
        comment
    )
    
    if success:
        await update.effective_chat.send_message(
            f"✅ Запись успешно создана!\n\n"
            f"👤 Имя: {context.user_data['client_name']}\n"
            f"🛞 Размер колёс: R{context.user_data['wheel_size']}\n"
            f"📅 Дата: {context.user_data['date']}\n"
            f"⏰ Время: {context.user_data['time']}\n"
            f"💬 Комментарий: (не добавлен)\n\n"
            f"Ждём вас!"
        )
    else:
        await update.effective_chat.send_message(
            "❌ Ошибка при создании записи. Попробуйте позже."
        )
    
    context.user_data.clear()

async def my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать записи пользователя"""
    user_id = update.effective_user.id
    bookings = get_user_bookings(user_id)
    
    if not bookings:
        await update.message.reply_text("📭 У вас нет активных записей.")
        return
    
    text = "📋 Ваши записи:\n\n"
    for i, booking in enumerate(bookings, 1):
        text += (
            f"{i}. 👤 {booking.get('Имя клиента', 'N/A')}\n"
            f"   🛞 {booking['Размер колес']} | "
            f"📅 {booking['Дата']} ⏰ {booking['Время']}\n\n"
        )
    
    await update.message.reply_text(text)

async def cancel_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса отмены записи"""
    user_id = update.effective_user.id
    bookings = get_user_bookings(user_id)
    
    if not bookings:
        await update.message.reply_text("📭 У вас нет активных записей для отмены.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Выберите запись для отмены:",
        reply_markup=get_cancel_booking_keyboard(bookings)
    )
    return CANCEL_SELECTING

async def cancel_booking_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка отмены выбранной записи"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "cancel_back":
        await query.edit_message_text("❌ Отмена отменена.")
        return ConversationHandler.END
    
    parts = query.data.replace("cancel_", "").split("_")
    date = parts[0]
    time = parts[1]
    
    user_id = update.effective_user.id
    success = cancel_booking(user_id, date, time)
    
    if success:
        await query.edit_message_text(
            f"✅ Запись на {date} в {time} успешно отменена."
        )
    else:
        await query.edit_message_text(
            "❌ Ошибка при отмене записи. Попробуйте позже."
        )
    
    return ConversationHandler.END

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена диалога"""
    await update.message.reply_text("❌ Действие отменено.")
    context.user_data.clear()
    return ConversationHandler.END
