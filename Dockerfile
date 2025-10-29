FROM python:3.11-slim

WORKDIR /app

# Копируем все файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir python-telegram-bot gspread google-auth google-auth-oauthlib google-auth-httplib2

# Запускаем бота
CMD ["python", "main.py"]
