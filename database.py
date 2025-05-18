import sqlite3
import json
from datetime import datetime

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    # Создаем единую таблицу для всех типов скважин
    c.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            depth REAL NOT NULL,
            type INTEGER NOT NULL,  -- 1: наклонная, 2: горизонтальная
            profile_type INTEGER NOT NULL,  -- для наклонных: 1-3инт, 2-4инт, 3-J, 4-S; для горизонтальных: 0
            type_ha INTEGER NOT NULL,  -- для наклонных: 0; для горизонтальных: 1-5
            type_h INTEGER NOT NULL,  -- для наклонных: 0; для горизонтальных: 1-4
            timestamp DATETIME NOT NULL,
            results TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_calculation_results(depth, well_type, profile_type, type_ha, type_h, results):
    """
    Сохранение результатов расчета в базу данных
    
    Args:
        depth: глубина скважины
        well_type: тип скважины (1 - наклонная, 2 - горизонтальная)
        profile_type: тип профиля (для наклонных: 1-3инт, 2-4инт, 3-J, 4-S; для горизонтальных: 0)
        type_ha: тип горизонтального аппарата (для наклонных: 0; для горизонтальных: 1-5)
        type_h: тип горизонтального аппарата (для наклонных: 0; для горизонтальных: 1-4)
        results: результаты расчета
    
    Returns:
        int: ID сохраненного расчета
    """
    print(f"Сохранение расчета: depth={depth}, well_type={well_type}, profile_type={profile_type}")
    
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    c.execute('''
    INSERT INTO calculations (depth, type, profile_type, type_ha, type_h, timestamp, results)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (depth, well_type, profile_type, type_ha, type_h, datetime.now(), json.dumps(results)))
    
    calculation_id = c.lastrowid
    conn.commit()
    conn.close()
    return calculation_id

def get_calculation_results(calculation_id):
    """
    Получение результатов расчета из базы данных
    
    Args:
        calculation_id: ID расчета
    
    Returns:
        dict: словарь с данными таблицы
    """
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM calculations WHERE id = ?', (calculation_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'depth': row[1],
            'type': row[2],
            'profile_type': row[3],
            'type_ha': row[4],
            'type_h': row[5],
            'timestamp': row[6],
            'results': json.loads(row[7])
        }
    return None

def get_all_calculations():
    """
    Получение списка всех расчетов
    
    Returns:
        list: список словарей с информацией о расчетах
    """
    print("Получение списка всех расчетов")
    
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM calculations ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'depth': row[1],
        'type': row[2],
        'profile_type': row[3],
        'type_ha': row[4],
        'type_h': row[5],
        'timestamp': row[6],
        'results': json.loads(row[7])
    } for row in rows]

def delete_calculation(calculation_id):
    """
    Удаление расчета из базы данных
    
    Args:
        calculation_id: ID расчета для удаления
    """
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    c.execute('DELETE FROM calculations WHERE id = ?', (calculation_id,))
    conn.commit()
    conn.close()

def clear_database():
    """
    Очистка всей базы данных - удаление всех записей из таблицы calculations
    """
    conn = sqlite3.connect('well_calculations.db')
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM calculations')
        conn.commit()
        print("База данных успешно очищена")
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {str(e)}")
        conn.rollback()
    finally:
        conn.close() 