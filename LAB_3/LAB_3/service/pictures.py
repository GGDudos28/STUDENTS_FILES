"""
Уровень сервиса: бизнес-логика работы с изображениями.
Содержит функции обработки изображений с помощью OpenCV.
"""
import cv2
import numpy as np
from model.pictures import Picture
import data.pictures as pictures_data


def get_all() -> list[Picture]:
    """Получает все изображения."""
    return pictures_data.get_all()


def get_one(name: str) -> Picture | None:
    """
    Получает одно изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        Picture | None: объект изображения или None
    """
    return pictures_data.get_one(name=name)


def add_one(picture: Picture) -> int:
    """
    Сохраняет объект Picture в базу данных.
    
    Args:
        picture: объект Picture
    
    Returns:
        int: ID новой записи
    """
    return pictures_data.add_one(picture)


def update_one(name: str, description: str) -> bool:
    """
    Обновляет описание изображения.
    
    Args:
        name: имя изображения
        description: новое описание
    
    Returns:
        bool: True если обновление выполнено
    """
    return pictures_data.update_one(name, description)


def delete_one(name: str) -> bool:
    """
    Удаляет изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        bool: True если удаление выполнено
    """
    return pictures_data.delete_one(name)


def to_grayscale(picture: Picture) -> Picture:
    """
    Преобразует изображение в градации серого.
    
    Алгоритм:
    1. cv2.cvtColor() конвертирует BGR в серый
    2. cv2.cvtColor() конвертирует обратно в 3-канальный формат для совместимости
    
    Args:
        picture: исходное изображение
    
    Returns:
        Picture: новое изображение в градациях серого
    """
    # Конвертируем в grayscale
    gray = cv2.cvtColor(picture.img, cv2.COLOR_BGR2GRAY)
    # Конвертируем обратно в 3-канальный формат (для совместимости)
    gray_3channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    
    return Picture(
        name=f"gray_{picture.name}",
        img=gray_3channel,
        description=f"Grayscale version of {picture.name}",
        dt=picture.dt
    )


def detect_edges(picture: Picture, threshold1: int = 100, threshold2: int = 200) -> Picture:
    """
    Выделяет границы на изображении с помощью алгоритма Canny.
    
    Алгоритм Canny:
    - threshold1: нижний порог для гистерезиса
    - threshold2: верхний порог для гистерезиса
    
    Args:
        picture: исходное изображение
        threshold1: нижний порог
        threshold2: верхний порог
    
    Returns:
        Picture: изображение с выделенными границами
    """
    # Конвертируем в grayscale для лучшего выделения границ
    gray = cv2.cvtColor(picture.img, cv2.COLOR_BGR2GRAY)
    # Применяем детектор границ Canny
    edges = cv2.Canny(gray, threshold1, threshold2)
    # Конвертируем обратно в 3-канальный формат
    edges_3channel = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    return Picture(
        name=f"edges_{picture.name}",
        img=edges_3channel,
        description=f"Edge detection (Canny) of {picture.name}",
        dt=picture.dt
    )


def apply_blur(picture: Picture, kernel_size: tuple = (5, 5)) -> Picture:
    """
    Применяет Gaussian blur к изображению.
    
    Gaussian blur используется для:
    - уменьшения шума
    - сглаживания изображения
    
    Args:
        picture: исходное изображение
        kernel_size: размер ядра (должен быть нечетным)
    
    Returns:
        Picture: размытое изображение
    """
    # Применяем Gaussian blur
    blurred = cv2.GaussianBlur(picture.img, kernel_size, 0)
    
    return Picture(
        name=f"blur_{picture.name}",
        img=blurred,
        description=f"Gaussian blurred version of {picture.name} (kernel={kernel_size})",
        dt=picture.dt
    )