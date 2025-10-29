from config import get_google_sheet
from datetime import datetime, timedelta

def save_booking(user_id, username, client_name, wheel_size, date, time, comment=""):
    """Сохранение записи в Google Sheets"""
    try:
        print(f"[DEBUG] Попытка сохранить запись...")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return False
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = [
            str(user_id),
            username or "Не указано",
            client_name or "Не указано",
            f"R{wheel_size}",
            date,
            time,
            "Активна",
            timestamp,
            comment or "-"
        ]
        
        print(f"[DEBUG] Добавляем строку: {row}")
        sheet.append_row(row)
        print("[SUCCESS] Запись добавлена в таблицу!")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка сохранения: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_user_bookings(user_id):
    """Получение всех записей пользователя"""
    try:
        print(f"[DEBUG] Получаем записи для пользователя {user_id}")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        print(f"[DEBUG] Таблица получена, читаем все записи...")
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая или нет данных")
            return []
        
        headers = all_values[0]
        print(f"[DEBUG] Заголовки: {headers}")
        
        user_bookings = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                user_id_cell = str(row[0]).strip()
                status_cell = str(row[6]).strip()
                
                if user_id_cell == str(user_id) and status_cell == 'Активна':
                    booking = {
                        'ID пользователя': row[0],
                        'Username': row[1],
                        'Имя клиента': row[2],
                        'Размер колес': row[3],
                        'Дата': row[4],
                        'Время': row[5],
                        'Статус': row[6]
                    }
                    user_bookings.append(booking)
                    print(f"[DEBUG] ✓ Найдена запись: {booking}")
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        # Сортируем по дате и времени
        user_bookings.sort(key=lambda x: (x['Дата'], x['Время']))
        
        print(f"[DEBUG] Найдено записей: {len(user_bookings)}")
        return user_bookings
    except Exception as e:
        print(f"[ERROR] Ошибка получения записей: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_booked_times(date):
    """Получение занятых времён на конкретную дату"""
    try:
        print(f"[DEBUG] Получаем занятые времена для даты: {date}")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return []
        
        booked = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                record_date = str(row[4]).strip()
                record_time = str(row[5]).strip()
                status = str(row[6]).strip()
                
                if record_date == date and status == 'Активна':
                    booked.append(record_time)
                    print(f"[DEBUG] Время {record_time} занято")
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        print(f"[DEBUG] Всего занято времен: {len(booked)}")
        return booked
    except Exception as e:
        print(f"[ERROR] Ошибка получения времени: {e}")
        import traceback
        traceback.print_exc()
        return []

def cancel_booking(user_id, date, time):
    """Отмена записи пользователя"""
    try:
        print(f"[DEBUG] Отмена записи: user_id={user_id}, date={date}, time={time}")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return False
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return False
        
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                if (str(row[0]).strip() == str(user_id) and 
                    str(row[4]).strip() == date and 
                    str(row[5]).strip() == time and 
                    str(row[6]).strip() == 'Активна'):
                    sheet.update_cell(i, 7, 'Отменена')
                    print(f"[DEBUG] Запись отменена в строке {i}")
                    return True
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        print("[ERROR] Запись для отмены не найдена")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка отмены: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_today_bookings():
    """Получение записей на сегодня (только будущие записи)"""
    today = datetime.now().strftime("%d.%m.%Y")
    current_time = datetime.now().strftime("%H:%M")
    
    try:
        print(f"[DEBUG] Получаем записи на сегодня: {today} (текущее время: {current_time})")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return []
        
        today_bookings = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                record_date = str(row[4]).strip()
                record_time = str(row[5]).strip()
                status = str(row[6]).strip()
                
                if record_date == today and status == 'Активна':
                    # Проверяем, что время ещё не прошло
                    if record_time >= current_time:
                        booking = {
                            'ID пользователя': row[0],
                            'Username': row[1],
                            'Имя клиента': row[2],
                            'Размер колес': row[3],
                            'Дата': row[4],
                            'Время': row[5],
                            'Статус': row[6]
                        }
                        today_bookings.append(booking)
                        print(f"[DEBUG] ✓ Запись добавлена: {record_time}")
                    else:
                        print(f"[DEBUG] ✗ Время {record_time} уже прошло")
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        # Сортируем по времени
        today_bookings.sort(key=lambda x: x['Время'])
        
        print(f"[DEBUG] Записей на сегодня: {len(today_bookings)}")
        return today_bookings
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_tomorrow_bookings():
    """Получение записей на завтра"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")
    try:
        print(f"[DEBUG] Получаем записи на завтра: {tomorrow}")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return []
        
        tomorrow_bookings = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                record_date = str(row[4]).strip()
                status = str(row[6]).strip()
                
                if record_date == tomorrow and status == 'Активна':
                    booking = {
                        'ID пользователя': row[0],
                        'Username': row[1],
                        'Имя клиента': row[2],
                        'Размер колес': row[3],
                        'Дата': row[4],
                        'Время': row[5],
                        'Статус': row[6]
                    }
                    tomorrow_bookings.append(booking)
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        # Сортируем по времени
        tomorrow_bookings.sort(key=lambda x: x['Время'])
        
        print(f"[DEBUG] Записей на завтра: {len(tomorrow_bookings)}")
        return tomorrow_bookings
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_week_bookings():
    """Получение записей на неделю (7 дней вперёд), отсортированные по дате и времени"""
    try:
        print(f"[DEBUG] Получаем записи на неделю")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return []
        
        # Генерируем даты на неделю вперёд
        week_dates = []
        for i in range(7):
            date = (datetime.now() + timedelta(days=i)).strftime("%d.%m.%Y")
            week_dates.append(date)
        
        print(f"[DEBUG] Даты недели: {week_dates}")
        
        week_bookings = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                record_date = str(row[4]).strip()
                status = str(row[6]).strip()
                
                if record_date in week_dates and status == 'Активна':
                    booking = {
                        'ID пользователя': row[0],
                        'Username': row[1],
                        'Имя клиента': row[2],
                        'Размер колес': row[3],
                        'Дата': row[4],
                        'Время': row[5],
                        'Статус': row[6]
                    }
                    week_bookings.append(booking)
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        # Сортируем по дате и времени
        week_bookings.sort(key=lambda x: (x['Дата'], x['Время']))
        
        print(f"[DEBUG] Записей на неделю: {len(week_bookings)}")
        return week_bookings
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_all_active_bookings():
    """Получение всех активных записей (для админ-удаления)"""
    try:
        print(f"[DEBUG] Получаем все активные записи для удаления")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return []
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return []
        
        all_bookings = []
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                status = str(row[6]).strip()
                
                if status == 'Активна':
                    booking = {
                        'row_number': i,
                        'ID пользователя': row[0],
                        'Username': row[1],
                        'Имя клиента': row[2],
                        'Размер колес': row[3],
                        'Дата': row[4],
                        'Время': row[5],
                        'Статус': row[6]
                    }
                    all_bookings.append(booking)
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        # Сортируем по дате и времени
        all_bookings.sort(key=lambda x: (x['Дата'], x['Время']))
        
        print(f"[DEBUG] Всего активных записей: {len(all_bookings)}")
        return all_bookings
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return []

def admin_delete_booking(date, time):
    """Удаление записи админом"""
    try:
        print(f"[DEBUG] Админ удаляет запись: date={date}, time={time}")
        sheet = get_google_sheet()
        if not sheet:
            print("[ERROR] Не удалось получить доступ к таблице!")
            return False
        
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 2:
            print("[DEBUG] Таблица пустая")
            return False
        
        for i, row in enumerate(all_values[1:], start=2):
            try:
                if len(row) < 7:
                    continue
                    
                if (str(row[4]).strip() == date and 
                    str(row[5]).strip() == time and 
                    str(row[6]).strip() == 'Активна'):
                    sheet.update_cell(i, 7, 'Удалена')
                    print(f"[DEBUG] Запись удалена в строке {i}")
                    return True
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке строки {i}: {e}")
                continue
        
        print("[ERROR] Запись для удаления не найдена")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка удаления: {e}")
        import traceback
        traceback.print_exc()
        return False