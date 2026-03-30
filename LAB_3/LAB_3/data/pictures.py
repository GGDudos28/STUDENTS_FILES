"""
Уровень данных: прямое взаимодействие с SQLite через DB-API.
Выполняет CRUD операции с изображениями.
"""
import numpy as np
import cv2
from datetime import datetime
from .init import conn, curs
from model.pictures import Picture


def row_to_model(row: tuple) -> Picture | None:
    """
    Преобразует строку из БД в объект Picture.
    
    Процесс:
    1. Извлекаем BLOB (image_data) из строки
    2. Преобразуем BLOB в numpy array с помощью cv2.imdecode
    3. Создаем объект Picture
    
    Args:
        row: кортеж из БД (id, name, description, image_data, created_at)
    
    Returns:
        Picture | None: объект изображения или None
    """
    if row is None:
        return None
    
    # row[3] - это image_data (BLOB)
    image_bytes = row[3]
    # Преобразуем байты в numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    # Декодируем изображение обратно в OpenCV формат
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    return Picture(
        name=row[1],
        img=img,
        description=row[2] or "",
        dt=datetime.strptime(row[4], '%Y-%m-%d %H:%M:%S') if row[4] else datetime.now()
    )


def get_all() -> list[Picture]:
    """
    Получает все изображения из базы данных.
    
    Returns:
        list[Picture]: список всех изображений
    """
    qry = "SELECT * FROM pictures ORDER BY created_at DESC"
    curs.execute(qry)
    rows = curs.fetchall()
    return [row_to_model(row) for row in rows if row_to_model(row) is not None]


def get_one(name: str) -> Picture | None:
    """
    Получает одно изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        Picture | None: объект изображения или None
    """
    qry = "SELECT * FROM pictures WHERE name = ?"
    curs.execute(qry, (name,))
    row = curs.fetchone()
    return row_to_model(row)


def add_one(picture: Picture) -> int:
    """
    Сохраняет объект Picture в базу данных.
    
    Процесс:
    1. Кодируем numpy array в PNG формат
    2. Преобразуем в BLOB (bytes)
    3. Выполняем INSERT
    
    Args:
        picture: объект Picture
    
    Returns:
        int: ID новой записи
    """
    # Кодируем изображение в PNG формат
    success, encoded_img = cv2.imencode('.png', picture.img)
    if not success:
        raise ValueError("Не удалось закодировать изображение")
    
    # Преобразуем в BLOB
    image_blob = encoded_img.tobytes()
    
    # Форматируем дату для SQLite
    created_at_str = picture.dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Выполняем INSERT (используем INSERT OR REPLACE для обновления существующих)
    curs.execute('''
        INSERT OR REPLACE INTO pictures (name, description, image_data, created_at)
        VALUES (?, ?, ?, ?)
    ''', (picture.name, picture.description, image_blob, created_at_str))
    
    conn.commit()
    return curs.lastrowid


def update_one(name: str, description: str) -> bool:
    """
    Обновляет описание изображения по имени.
    
    Args:
        name: имя изображения
        description: новое описание
    
    Returns:
        bool: True если обновление выполнено, False если изображение не найдено
    """
    # Проверяем существование записи
    curs.execute("SELECT id FROM pictures WHERE name = ?", (name,))
    if curs.fetchone() is None:
        return False
    
    # Обновляем описание
    curs.execute('''
        UPDATE pictures 
        SET description = ? 
        WHERE name = ?
    ''', (description, name))
    
    conn.commit()
    return True


def delete_one(name: str) -> bool:
    """
    Удаляет изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        bool: True если удаление выполнено, False если изображение не найдено
    """
    # Проверяем существование записи
    curs.execute("SELECT id FROM pictures WHERE name = ?", (name,))
    if curs.fetchone() is None:
        return False
    
    # Удаляем запись
    curs.execute("DELETE FROM pictures WHERE name = ?", (name,))
    conn.commit()
    return True