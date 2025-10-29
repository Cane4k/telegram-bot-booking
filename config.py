import gspread
from google.oauth2.service_account import Credentials

# ===== ВАШИ ДАННЫЕ =====

# Токен вашего Telegram бота
TELEGRAM_TOKEN = '8209144917:AAG2qYOP-nlcV5_WYnC32qsW1DtTdB3g04o'

# ID администраторов (ваш Telegram ID)
ADMIN_IDS = [535852355]

# ===== НАСТРОЙКА GOOGLE SHEETS =====

SCOPE = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_sheet():
    """Подключение к Google Sheets"""
    try:
        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=SCOPE
        )
        client = gspread.authorize(creds)
        
        # Ваша Google Таблица
        sheet = client.open("Шиномонтаж").sheet1
        return sheet
    except Exception as e:
        print(f"[ERROR] Ошибка подключения к Google Sheets: {e}")
        return None

# ===== НАСТРОЙКИ БИЗНЕС-ЛОГИКИ =====

# Доступные размеры колёс
WHEEL_SIZES = ["13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]

# Рабочие часы (с 8:00 до 21:30, шаг 30 минут)
WORKING_HOURS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
    "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
    "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
    "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
    "20:00", "20:30", "21:00", "21:30"
]
