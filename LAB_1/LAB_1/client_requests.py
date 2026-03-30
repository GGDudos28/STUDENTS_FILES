"""
Клиент для тестирования API с помощью библиотеки requests
Демонстрирует отправку запросов к эндпоинтам обработки изображений
"""

import requests
import sys
import os

# Базовый URL сервера
BASE_URL = "http://localhost:8000"


def test_health():
    """Тестирование базовых эндпоинтов"""
    print("\n=== Тестирование базовых эндпоинтов ===")
    
    # GET /hi
    response = requests.get(f"{BASE_URL}/hi")
    print(f"GET /hi: {response.status_code} - {response.json()}")
    
    # GET /hi/John (path parameter)
    response = requests.get(f"{BASE_URL}/hi/John")
    print(f"GET /hi/John: {response.status_code} - {response.json()}")
    
    # GET /hi_q?who=John (query parameter)
    response = requests.get(f"{BASE_URL}/hi_q", params={"who": "John"})
    print(f"GET /hi_q?who=John: {response.status_code} - {response.json()}")
    
    # POST /hi_body (JSON body)
    response = requests.post(f"{BASE_URL}/hi_body", json={"who": "John"})
    print(f"POST /hi_body: {response.status_code} - {response.json()}")


def test_image_processing(input_image_path, mode="edges", max_size=512):
    """
    Тестирование основного эндпоинта обработки изображений
    
    Args:
        input_image_path: путь к исходному изображению
        mode: режим обработки (gray, edges, blur)
        max_size: максимальный размер
    """
    print(f"\n=== Тестирование обработки изображения (mode={mode}) ===")
    
    # Проверка существования файла
    if not os.path.exists(input_image_path):
        print(f"Ошибка: файл {input_image_path} не найден!")
        return
    
    # Открываем файл и отправляем
    with open(input_image_path, "rb") as f:
        # files - для multipart/form-data
        files = {
            "image": (os.path.basename(input_image_path), f, "image/jpeg")
        }
        # params - query-параметры
        params = {
            "mode": mode,
            "max_size": max_size
        }
        
        # Отправляем POST запрос
        response = requests.post(
            f"{BASE_URL}/image/process",
            files=files,
            params=params
        )
        
        # Выводим информацию об ответе
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"X-Processed-Mode: {response.headers.get('x-processed-mode')}")
        
        # Сохраняем результат
        if response.status_code == 200:
            output_path = f"out_{mode}.png"
            with open(output_path, "wb") as out:
                out.write(response.content)
            print(f"✅ Изображение сохранено как {output_path}")
        else:
            print(f"❌ Ошибка: {response.text}")


def test_preprocess(input_image_path, mode="threshold", student_id="ST12345"):
    """
    Тестирование самостоятельного задания (эндпоинт /image/preprocess)
    
    Args:
        input_image_path: путь к исходному изображению
        mode: режим обработки (gray, threshold, edges)
        student_id: ID студента (передается в заголовке)
    """
    print(f"\n=== Тестирование препроцессинга (mode={mode}, student_id={student_id}) ===")
    
    if not os.path.exists(input_image_path):
        print(f"Ошибка: файл {input_image_path} не найден!")
        return
    
    with open(input_image_path, "rb") as f:
        files = {"image": (os.path.basename(input_image_path), f, "image/jpeg")}
        params = {"mode": mode}
        # Заголовки передаются отдельно
        headers = {"X-Student-Id": student_id}
        
        response = requests.post(
            f"{BASE_URL}/image/preprocess",
            files=files,
            params=params,
            headers=headers
        )
        
        print(f"Status code: {response.status_code}")
        print(f"X-Processed-Mode: {response.headers.get('x-processed-mode')}")
        print(f"X-Student-Id: {response.headers.get('x-student-id')}")
        
        if response.status_code == 200:
            output_path = f"preprocess_{mode}.png"
            with open(output_path, "wb") as out:
                out.write(response.content)
            print(f"✅ Изображение сохранено как {output_path}")
        else:
            print(f"❌ Ошибка: {response.text}")


def main():
    """Основная функция для запуска тестов"""
    
    # Проверяем наличие аргумента командной строки с путем к изображению
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Если путь не указан, создаем тестовое изображение
        from PIL import Image, ImageDraw
        test_image_path = "test_input.jpg"
        
        # Создаем тестовое изображение размером 800x600
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Рисуем простые фигуры для теста
        draw.rectangle([100, 100, 300, 200], fill='red')
        draw.rectangle([400, 100, 600, 200], fill='green')
        draw.ellipse([100, 300, 300, 500], fill='blue')
        draw.ellipse([400, 300, 600, 500], fill='yellow')
        
        img.save(test_image_path, 'JPEG')
        image_path = test_image_path
        print(f"Создано тестовое изображение: {image_path}")
    
    print(f"Используется изображение: {image_path}")
    
    # Запускаем тесты
    test_health()
    
    # Тестируем разные режимы обработки
    test_image_processing(image_path, mode="gray")
    test_image_processing(image_path, mode="edges")
    test_image_processing(image_path, mode="blur")
    
    # Тестируем самостоятельное задание
    test_preprocess(image_path, mode="gray", student_id="IVANOV_2024")
    test_preprocess(image_path, mode="edges", student_id="IVANOV_2024")
    test_preprocess(image_path, mode="threshold", student_id="IVANOV_2024")
    
    print("\n=== Все тесты завершены ===")


if __name__ == "__main__":
    main()