"""
Pydantic-модели для валидации и сериализации данных.
Модель Picture представляет изображение с метаданными.
"""
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime


class Picture(BaseModel):
    """
    Модель изображения.
    
    Атрибуты:
        name: имя файла изображения
        img: изображение в виде numpy array (BGR формат OpenCV)
        description: текстовое описание изображения
        dt: дата и время создания записи
    """
    name: str
    img: np.ndarray
    description: str = ""
    dt: datetime = Field(default_factory=datetime.now)
    
    model_config = {
        "arbitrary_types_allowed": True  # Разрешаем использование np.ndarray
    }