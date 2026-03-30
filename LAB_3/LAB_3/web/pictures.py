"""
Уровень представления: FastAPI роутеры для работы с изображениями.
Обрабатывает HTTP запросы и возвращает ответы.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
import cv2
import numpy as np
from service.pictures import (
    add_one, get_one, delete_one, update_one,
    to_grayscale, detect_edges, apply_blur, get_all
)
from model.pictures import Picture
from datetime import datetime
from pydantic import BaseModel


class DescriptionUpdate(BaseModel):
    """Модель для обновления описания."""
    description: str


router = APIRouter(prefix="/pictures", tags=["pictures"])


@router.get("/", response_model=list[dict])
async def list_pictures():
    """
    Получает список всех изображений.
    
    Returns:
        Список метаданных всех изображений
    """
    pictures = get_all()
    return [
        {
            "name": p.name,
            "description": p.description,
            "created_at": p.dt.isoformat()
        }
        for p in pictures
    ]


@router.post("/", status_code=201)
async def upload_picture(file: UploadFile = File(...)):
    """
    Загружает новое изображение.
    
    Процесс:
    1. Читает байты файла
    2. Преобразует в numpy array
    3. Декодирует в OpenCV формат
    4. Сохраняет в БД
    
    Args:
        file: загружаемый файл изображения
    
    Returns:
        Сообщение об успешной загрузке
    """
    # Проверяем тип файла
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")
    
    # Читаем содержимое файла
    contents = await file.read()
    
    # Преобразуем байты в numpy array
    nparr = np.frombuffer(contents, np.uint8)
    # Декодируем изображение
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise HTTPException(status_code=400, detail="Не удалось декодировать изображение")
    
    # Создаем объект Picture
    picture = Picture(
        name=file.filename,
        img=img,
        description="",
        dt=datetime.now()
    )
    
    # Сохраняем в БД
    picture_id = add_one(picture)
    
    return {
        "message": "Изображение успешно сохранено",
        "id": picture_id,
        "name": file.filename
    }


@router.get("/{name}")
async def get_picture(name: str):
    """
    Получает изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        PNG изображение или сообщение об ошибке
    """
    picture = get_one(name)
    if picture is None:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    # Кодируем изображение в PNG
    success, encoded_img = cv2.imencode('.png', picture.img)
    if not success:
        raise HTTPException(status_code=500, detail="Не удалось закодировать изображение")
    
    return Response(
        content=encoded_img.tobytes(),
        media_type="image/png"
    )


@router.patch("/{name}")
async def update_picture_description(name: str, update: DescriptionUpdate):
    """
    Обновляет описание изображения.
    
    Args:
        name: имя изображения
        update: новое описание
    
    Returns:
        Обновленный объект изображения
    """
    # Обновляем описание
    success = update_one(name, update.description)
    
    if not success:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    # Получаем обновленное изображение
    picture = get_one(name)
    
    return {
        "message": "Описание обновлено",
        "name": picture.name,
        "description": picture.description,
        "created_at": picture.dt.isoformat()
    }


@router.delete("/{name}")
async def delete_picture(name: str):
    """
    Удаляет изображение по имени.
    
    Args:
        name: имя изображения
    
    Returns:
        Сообщение об успешном удалении
    """
    success = delete_one(name)
    
    if not success:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    return {"message": f"Изображение '{name}' успешно удалено"}


@router.post("/{name}/grayscale")
async def picture_to_grayscale(name: str):
    """
    Преобразует изображение в градации серого.
    
    Args:
        name: имя исходного изображения
    
    Returns:
        Обработанное изображение в формате PNG
    """
    # Получаем исходное изображение
    original = get_one(name)
    if original is None:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    # Применяем обработку
    processed = to_grayscale(original)
    
    # Сохраняем обработанное изображение
    add_one(processed)
    
    # Возвращаем результат
    success, encoded_img = cv2.imencode('.png', processed.img)
    return Response(
        content=encoded_img.tobytes(),
        media_type="image/png"
    )


@router.post("/{name}/edges")
async def picture_detect_edges(
    name: str,
    threshold1: int = 100,
    threshold2: int = 200
):
    """
    Выделяет границы на изображении (Canny edge detection).
    
    Args:
        name: имя исходного изображения
        threshold1: нижний порог Canny
        threshold2: верхний порог Canny
    
    Returns:
        Обработанное изображение в формате PNG
    """
    # Получаем исходное изображение
    original = get_one(name)
    if original is None:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    # Применяем обработку
    processed = detect_edges(original, threshold1, threshold2)
    
    # Сохраняем обработанное изображение
    add_one(processed)
    
    # Возвращаем результат
    success, encoded_img = cv2.imencode('.png', processed.img)
    return Response(
        content=encoded_img.tobytes(),
        media_type="image/png"
    )


@router.post("/{name}/blur")
async def picture_apply_blur(
    name: str,
    kernel_size: int = 5
):
    """
    Применяет Gaussian blur к изображению.
    
    Args:
        name: имя исходного изображения
        kernel_size: размер ядра размытия (нечетное число)
    
    Returns:
        Обработанное изображение в формате PNG
    """
    # Проверяем, что kernel_size нечетный
    if kernel_size % 2 == 0:
        kernel_size += 1
    
    # Получаем исходное изображение
    original = get_one(name)
    if original is None:
        raise HTTPException(status_code=404, detail="Изображение не найдено")
    
    # Применяем обработку
    processed = apply_blur(original, (kernel_size, kernel_size))
    
    # Сохраняем обработанное изображение
    add_one(processed)
    
    # Возвращаем результат
    success, encoded_img = cv2.imencode('.png', processed.img)
    return Response(
        content=encoded_img.tobytes(),
        media_type="image/png"
    )