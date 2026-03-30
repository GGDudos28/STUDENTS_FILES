"""
Главный файл приложения FastAPI.
Инициализирует приложение и подключает роутеры.
"""
from fastapi import FastAPI
from web.pictures import router as pictures_router

app = FastAPI(
    title="FastAPI Image Processing Lab",
    description="Лабораторная работа по обработке изображений с FastAPI и OpenCV",
    version="1.0.0"
)

# Подключаем роутеры
app.include_router(pictures_router)


@app.get('/')
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "FastAPI Image Processing Lab",
        "endpoints": {
            "pictures": "/pictures",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)