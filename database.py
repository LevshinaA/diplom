import sqlite3
from datetime import datetime

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    
    # Проверяем существующую структуру таблицы
    c.execute("PRAGMA table_info(calculations)")
    columns = [column[1] for column in c.fetchall()]
    
    if not columns:
        # Если таблица не существует, создаем новую
        c.execute('''
            CREATE TABLE calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                depth REAL,
                profile_type INTEGER, -- 1 - трехинтервальный, 2 - четырехинтервальный
                timestamp DATETIME,
                results TEXT
            )
        ''')
    elif 'displacement' in columns:
        # Сначала удаляем таблицу calculations_new, если она существует
        c.execute('DROP TABLE IF EXISTS calculations_new')
        
        # Создаем новую таблицу
        c.execute('''
            CREATE TABLE calculations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                depth REAL,
                profile_type INTEGER, -- 1 - трехинтервальный, 2 - четырехинтервальный
                timestamp DATETIME,
                results TEXT
            )
        ''')
        
        # Копируем существующие данные с преобразованием
        c.execute('''
            INSERT INTO calculations_new (id, depth, profile_type, timestamp, results)
            SELECT 
                id,
                depth,
                1, -- устанавливаем тип 1 для существующих расчетов
                timestamp,
                results
            FROM calculations
        ''')
        
        # Удаляем старую таблицу и переименовываем новую
        c.execute('DROP TABLE calculations')
        c.execute('ALTER TABLE calculations_new RENAME TO calculations')
    
    conn.commit()
    conn.close()

def save_calculation_results(depth, profile_type, results):
    """
    Сохранение результатов расчета в базу данных
    
    Args:
        depth: глубина скважины
        profile_type: тип профиля (1 - трехинтервальный, 2 - четырехинтервальный)
        results: результаты расчета
    
    Returns:
        int: ID сохраненного расчета
    """
    print(f"Сохранение расчета: depth={depth}, profile_type={profile_type}")
    
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        c.execute('INSERT INTO calculations (depth, profile_type, timestamp, results) VALUES (?, ?, ?, ?)',
                 (depth, profile_type, timestamp, str(results)))
        calculation_id = c.lastrowid
        conn.commit()
        print(f"Расчет успешно сохранен с ID: {calculation_id}")
        return calculation_id
    except Exception as e:
        print(f"Ошибка при сохранении расчета: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_all_calculations():
    """
    Получение списка всех расчетов
    
    Returns:
        list: список словарей с информацией о расчетах
    """
    print("Получение списка всех расчетов")
    
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT id, depth, profile_type, timestamp FROM calculations ORDER BY timestamp DESC')
        calculations = []
        for row in c.fetchall():
            profile_type_str = "Трехинтервальный" if row[2] == 1 else "Четырехинтервальный"
            calculations.append({
                'id': row[0],
                'depth': row[1],
                'profile_type': row[2],
                'profile_type_str': profile_type_str,
                'timestamp': row[3]
            })
        print(f"Найдено {len(calculations)} расчетов")
        return calculations
        
    except Exception as e:
        print(f"Ошибка при получении расчетов: {str(e)}")
        raise
    finally:
        conn.close()

def get_calculation_results(calculation_id):
    """
    Получение результатов расчета из базы данных
    
    Args:
        calculation_id: ID расчета
    
    Returns:
        dict: словарь с данными таблицы
    """
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT depth, profile_type, timestamp, results FROM calculations WHERE id = ?', (calculation_id,))
        row = c.fetchone()
        
        if row:
            profile_type_str = "Трехинтервальный" if row[1] == 1 else "Четырехинтервальный"
            return {
                'depth': row[0],
                'profile_type': row[1],
                'profile_type_str': profile_type_str,
                'timestamp': row[2],
                'results': eval(row[3])
            }
        return None
        
    finally:
        conn.close()

def delete_calculation(calculation_id):
    """
    Удаление расчета из базы данных
    
    Args:
        calculation_id: ID расчета для удаления
    """
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM calculations WHERE id = ?', (calculation_id,))
        conn.commit()
    finally:
        conn.close() 