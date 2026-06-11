import sqlite3
import datetime

# Nazwa pliku bazy danych
DB_NAME = "historia_treningow.db"

# Tworzy plik bazy danych oraz domyślną tabelę
def init_db():
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()

        # Tabela wyników treningu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wyniki_serii (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_treningu TEXT,
                cwiczenie TEXT,
                seria INTEGER,
                poprawne INTEGER,
                bledne INTEGER,
                czas TEXT,
                sciezka_wideo TEXT
            )
        ''')

        conn.commit()
    finally:
        conn.close()

# Zapisuje wynik pojedynczej serii
def save_set_result(exercise, set_number, correct, incorrect, time_spent, video_path):
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
            INSERT INTO wyniki_serii (data_treningu, cwiczenie, seria, poprawne, bledne, czas, sciezka_wideo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (current_time, exercise, set_number, correct, incorrect, time_spent, video_path))

        conn.commit()
    finally:
        conn.close()

# Pobiera całą historię treningów od najnowszych
def get_all_results():
    conn = sqlite3.connect(DB_NAME)
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM wyniki_serii ORDER BY id DESC")
        results = cursor.fetchall()
        return results
    finally:
        conn.close()
