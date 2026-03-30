"""
Лабораторная работа №1: FastAPI и основы HTTP
Обработка изображений с помощью FastAPI и Pillow
ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

from fastapi import FastAPI, Body, Header, Response, UploadFile, File, HTTPException, Query
from fastapi.responses import Response
from PIL import Image, ImageOps, ImageFilter
import io

app = FastAPI(title="Lab01: HTTP + FastAPI")

# ==================== БАЗОВЫЕ ЭНДПОИНТЫ ====================

@app.get("/hi")
def greet():
    return "Hello? World?"

@app.get("/hi/{who}")
def greet_path(who: str):
    return f"Hello? {who}?"

@app.get("/hi_q")
def greet_query(who: str):
    return f"Hello? {who}?"

@app.post("/hi_body")
def greet_body(who: str = Body(embed=True)):
    return f"Hello? {who}?"

@app.get("/agent")
def get_agent(user_agent: str = Header(default="")):
    return f"Your User-Agent: {user_agent}"

@app.get("/header/{name}/{value}")
def set_header(name: str, value: str, response: Response):
    response.headers[name] = value
    return "normal body"

@app.post("/created", status_code=201)
def created_demo():
    return {"status": "created"}

# ==================== ОСНОВНОЕ ЗАДАНИЕ ====================

@app.post("/image/process")
async def process_image(
    image: UploadFile = File(...),
    mode: str = "gray",
    max_size: int = 512
):
    """Обработка изображения с различными эффектами"""
    
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type. Allowed: {allowed_types}"
        )
    
    raw = await image.read()
    img = Image.open(io.BytesIO(raw))
    img.thumbnail((max_size, max_size))
    
    if mode == "gray":
        img = ImageOps.grayscale(img)
    elif mode == "edges":
        img = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)
    elif mode == "blur":
        img = img.filter(ImageFilter.GaussianBlur(radius=2))
    else:
        raise HTTPException(
            status_code=422,
            detail="mode must be one of: gray, edges, blur"
        )
    
    out = io.BytesIO()
    img.save(out, format="PNG")
    
    return Response(
        content=out.getvalue(),
        media_type="image/png",
        headers={"X-Processed-Mode": mode}
    )

# ==================== САМОСТОЯТЕЛЬНОЕ ЗАДАНИЕ ====================

@app.post("/image/preprocess")
async def preprocess_image(
    student_id: str = Header(..., alias="X-Student-Id"),  # сначала параметры без default
    image: UploadFile = File(...),                         # параметры файла
    mode: str = "gray"                                     # параметр с default в конце
):
    """
    САМОСТОЯТЕЛЬНОЕ ЗАДАНИЕ:
    Предобработка изображений с поддержкой пороговой бинаризации
    """
    
    # Валидация MIME-типа
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail="Unsupported media type. Use JPEG, PNG, or WEBP"
        )
    
    # Чтение изображения
    raw = await image.read()
    img = Image.open(io.BytesIO(raw))
    
    # Применение обработки
    if mode == "gray":
        # Преобразование в оттенки серого
        img = ImageOps.grayscale(img)
        
    elif mode == "edges":
        # Поиск границ (сначала в серый, затем детектор краев)
        img = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)
        
    elif mode == "threshold":
        # Пороговая бинаризация
        # Шаг 1: преобразуем в оттенки серого
        img_gray = ImageOps.grayscale(img)
        # Шаг 2: применяем порог (128 - среднее значение)
        # point() применяет функцию к каждому пикселю
        # Если значение пикселя > порога -> 255 (белый), иначе -> 0 (черный)
        threshold_value = 128
        img = img_gray.point(lambda x: 255 if x > threshold_value else 0)
        
    else:
        raise HTTPException(
            status_code=422,
            detail="mode must be one of: gray, threshold, edges"
        )
    
    # Сохранение в байты
    out = io.BytesIO()
    img.save(out, format="PNG")
    
    # Возврат обработанного изображения
    return Response(
        content=out.getvalue(),
        media_type="image/png",
        headers={
            "X-Processed-Mode": mode,
            "X-Student-Id": student_id
        }
    )


# ==================== ДОПОЛНИТЕЛЬНО: РАСШИРЕННАЯ ВЕРСИЯ С QUERY ====================

@app.post("/image/preprocess_v2")
async def preprocess_image_v2(
    student_id: str = Header(..., alias="X-Student-Id"),
    image: UploadFile = File(...),
    mode: str = Query(..., description="Режим обработки: gray, threshold, edges"),  # обязательный
    threshold: int = Query(128, description="Порог для режима threshold")            # с default
):
    """
    Расширенная версия с возможностью указания порога через query-параметр
    """
    
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if image.content_type not in allowed_types:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    
    raw = await image.read()
    img = Image.open(io.BytesIO(raw))
    
    if mode == "gray":
        img = ImageOps.grayscale(img)
    elif mode == "edges":
        img = ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)
    elif mode == "threshold":
        img_gray = ImageOps.grayscale(img)
        img = img_gray.point(lambda x: 255 if x > threshold else 0)
    else:
        raise HTTPException(status_code=422, detail="Invalid mode")
    
    out = io.BytesIO()
    img.save(out, format="PNG")
    
    return Response(
        content=out.getvalue(),
        media_type="image/png",
        headers={
            "X-Processed-Mode": mode,
            "X-Student-Id": student_id,
            "X-Threshold": str(threshold) if mode == "threshold" else "N/A"
        }
    )