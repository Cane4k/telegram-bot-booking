from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from config import WHEEL_SIZES, WORKING_HOURS
from datetime import datetime, timedelta

# Список праздников (формат ДД.ММ.ГГГГ)
HOLIDAYS = [
    "01.01.2025",  # Новый год
    "02.01.2025",
    "03.01.2025",
    "04.01.2025",
    "05.01.2025",
    "06.01.2025",
    "07.01.2025",
    "08.01.2025",  # Рождество
    "23.02.2025",  # День защитника Отечества
    "08.03.2025",  # Международный женский день
    "01.05.2025",  # Праздник Весны и Труда
    "09.05.2025",  # День Победы
    "12.06.2025",  # День России
    "04.11.2025",  # День народного единства
]

def get_main_keyboard():
    """Главная клавиатура для пользователя"""
    keyboard = [
        ['📝 Записаться'],
        ['📋 Мои записи', '❌ Отменить запись']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_keyboard():
    """Клавиатура для администратора"""
    keyboard = [
        ['📅 Сегодня', '📆 Завтра'],
        ['📊 На неделю', '🗑 Удалить запись'],
        ['👤 Режим пользователя']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_wheel_size_keyboard():
    """Inline-клавиатура для выбора размера колёс"""
    keyboard = []
    row = []
    for i, size in enumerate(WHEEL_SIZES):
        row.append(InlineKeyboardButton(f"R{size}", callback_data=f"wheel_{size}"))
        if (i + 1) % 3 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

def get_date_keyboard():
    """Inline-клавиатура для выбора даты на ближайший месяц, исключая выходные и праздники"""
    keyboard = []
    today = datetime.now()
    
    for i in range(31):  # Ближайшие 31 день
        date = today + timedelta(days=i)
        date_str = date.strftime("%d.%m.%Y")
        weekday = date.weekday()  # 0=Пн, 6=Вс
        
        # Пропускаем выходные
        if weekday >= 5:
            continue
        
        # Пропускаем праздники
        if date_str in HOLIDAYS:
            continue
        
        # Формируем текст кнопки
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        button_text = f"{day_names[weekday]} {date_str}"
        
        if i == 0:
            button_text = f"Сегодня {date_str}"
        elif i == 1:
            button_text = f"Завтра {date_str}"
        
        keyboard.append([InlineKeyboardButton(
            button_text, 
            callback_data=f"date_{date_str}"
        )])
    
    return InlineKeyboardMarkup(keyboard)

def get_time_keyboard(booked_times=[]):
    """Inline-клавиатура для выбора времени (показывает только свободные)"""
    keyboard = []
    row = []
    available_count = 0
    
    for i, time in enumerate(WORKING_HOURS):
        # Показываем только свободные времена
        if time not in booked_times:
            row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
            available_count += 1
            
            # По 3 кнопки в ряду
            if (available_count) % 3 == 0:
                keyboard.append(row)
                row = []
    
    # Добавляем оставшиеся кнопки
    if row:
        keyboard.append(row)
    
    # Кнопка "Назад"
    keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_wheels")])
    return InlineKeyboardMarkup(keyboard)

def get_cancel_booking_keyboard(bookings):
    """Inline-клавиатура для выбора записи для отмены"""
    keyboard = []
    
    for booking in bookings:
        button_text = f"{booking['Размер колес']} | {booking['Дата']} {booking['Время']}"
        callback_data = f"cancel_{booking['Дата']}_{booking['Время']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel_back")])
    return InlineKeyboardMarkup(keyboard)

def get_delete_booking_keyboard(bookings):
    """Inline-клавиатура для выбора записи для удаления (для админа)"""
    keyboard = []
    
    for booking in bookings:
        button_text = f"{booking['Дата']} {booking['Время']} - {booking.get('Имя клиента', 'N/A')} ({booking['Размер колес']})"
        callback_data = f"admin_delete_{booking['Дата']}_{booking['Время']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="admin_delete_back")])
    return InlineKeyboardMarkup(keyboard)

def get_skip_comment_keyboard():
    """Inline-клавиатура для пропуска комментария"""
    keyboard = [
        [InlineKeyboardButton("⏭️ Пропустить", callback_data="skip_comment")]
    ]
    return InlineKeyboardMarkup(keyboard)
