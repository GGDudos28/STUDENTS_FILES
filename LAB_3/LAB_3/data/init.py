"""
Инициализация подключения к базе данных SQLite.
Использует DB-API (PEP 249) для работы с SQLite.
"""
import os
from pathlib import Path
from sqlite3 import connect, Connection, Cursor
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

conn: Connection | None = None
curs: Cursor | None = None


def get_db(name: str | None = None, reset: bool = False) -> None:
    """
    Подключается к файлу базы данных SQLite.
    
    Args:
        name: путь к файлу БД (если None, берется из .env)
        reset: если True, принудительно пересоздает подключение
    """
    global conn, curs
    
    # Если уже есть подключение и не требуется сброс - возвращаемся
    if conn and not reset:
        return
    
    # Определяем имя файла БД
    if not name:
        name = os.getenv("PICTURES_SQLITE_DB")
    
    # Если переменная окружения не задана, используем путь по умолчанию
    if not name:
        top_dir = Path(__file__).resolve().parents[1]
        db_dir = top_dir / "db"
        db_dir.mkdir(exist_ok=True)
        name = str(db_dir / "images.db")
    
    # Создаем подключение с отключенной проверкой потоков
    conn = connect(name, check_same_thread=False)
    curs = conn.cursor()
    print(f"Подключено к базе данных: {name}")


# Инициализируем подключение при импорте модуля
get_db()


def create_tables() -> None:
    """
    Создает необходимые таблицы в базе данных.
    Таблица pictures хранит изображения в формате BLOB.
    """
    get_db()
    curs.execute('''
        CREATE TABLE IF NOT EXISTS pictures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_data BLOB NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("Таблицы успешно созданы")


# Создаем таблицы при импорте
create_tables()