import sqlite3

DB_NAME = 'statistics.db'

def connect():
    return sqlite3.connect(DB_NAME)

def create_statistics_table():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            accuracy REAL NOT NULL,
            description TEXT
        )
        ''')
        conn.commit()

def add_statistic(accuracy, description):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO statistics (accuracy, description) VALUES (?, ?)', 
                       (accuracy, description))
        conn.commit()

def get_all_statistics():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, accuracy, description FROM statistics')
        return cursor.fetchall()

def get_statistic_by_id(stat_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, accuracy, description FROM statistics WHERE id = ?', 
                       (stat_id,))
        return cursor.fetchone()

def delete_statistic(stat_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM statistics WHERE id = ?', (stat_id,))
        conn.commit()
