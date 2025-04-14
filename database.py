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
                displacement REAL,
                timestamp DATETIME,
                results TEXT
            )
        ''')
    elif 'depth' not in columns:
        # Если существует старая структура, создаем новую таблицу и переносим данные
        c.execute('''
            CREATE TABLE calculations_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                depth REAL,
                displacement REAL,
                timestamp DATETIME,
                results TEXT
            )
        ''')
        
        # Копируем существующие данные с преобразованием
        c.execute('''
            INSERT INTO calculations_new (id, depth, displacement, timestamp, results)
            SELECT 
                c.id,
                COALESCE(r1.value, 0) as depth,
                COALESCE(r2.value, 0) as displacement,
                c.created_at as timestamp,
                '{}' as results
            FROM calculations c
            LEFT JOIN results r1 ON c.id = r1.calculation_id 
                AND r1.column_name = 'Глубина по вертикали, м'
                AND r1.row_number = 1
            LEFT JOIN results r2 ON c.id = r2.calculation_id 
                AND r2.column_name = 'Смещение, м'
                AND r2.row_number = 1
        ''')
        
        # Удаляем старые таблицы и переименовываем новую
        c.execute('DROP TABLE IF EXISTS results')
        c.execute('DROP TABLE calculations')
        c.execute('ALTER TABLE calculations_new RENAME TO calculations')
    
    conn.commit()
    conn.close()

def save_calculation_results(depth, displacement, results):
    """
    Сохранение результатов расчета в базу данных
    
    Args:
        depth: глубина скважины
        displacement: смещение
        results: результаты расчета
    
    Returns:
        int: ID сохраненного расчета
    """
    print(f"Сохранение расчета: depth={depth}, displacement={displacement}")
    
    conn = sqlite3.connect('calculations.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        c.execute('INSERT INTO calculations (depth, displacement, timestamp, results) VALUES (?, ?, ?, ?)',
                 (depth, displacement, timestamp, str(results)))
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
        c.execute('SELECT id, depth, displacement, timestamp FROM calculations ORDER BY timestamp DESC')
        calculations = [{'id': row[0], 'depth': row[1], 'displacement': row[2], 'timestamp': row[3]} 
                       for row in c.fetchall()]
        print(f"Найдено {len(calculations)} расчетов")
        for calc in calculations:
            print(f"Расчет {calc['id']}: depth={calc['depth']}, displacement={calc['displacement']}, timestamp={calc['timestamp']}")
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
        c.execute('SELECT depth, displacement, timestamp, results FROM calculations WHERE id = ?', (calculation_id,))
        row = c.fetchone()
        
        if row:
            return {
                'depth': row[0],
                'displacement': row[1],
                'timestamp': row[2],
                'results': eval(row[3])  # Преобразуем строку обратно в словарь
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