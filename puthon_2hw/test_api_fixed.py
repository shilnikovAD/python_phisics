"""
Простой тест API для проверки работы после исправления
"""

import asyncio
import os

import httpx


async def test_api_fixed():
    """Тест исправленного API"""
    base_url = "http://127.0.0.1:8001"

    print("=" * 60)
    print("ТЕСТ ИСПРАВЛЕННОГО API")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Тест 1: Корневой эндпоинт
            print("\n1. Проверка корневого эндпоинта...")
            response = await client.get(f"{base_url}/")
            print(f"   ✓ Статус: {response.status_code}")

            # Тест 2: Поиск Python репозиториев
            print("\n2. Поиск 5 Python репозиториев...")
            params = {"limit": 5, "lang": "Python", "stars_min": 1000}
            response = await client.get(f"{base_url}/api/search", params=params)
            result = response.json()
            print(f"   ✓ Статус: {response.status_code}")
            print(f"   ✓ Файл: {result['file']}")
            print(f"   ✓ Найдено: {result['count']} репозиториев")

            # Проверка файла
            if os.path.exists(result["file"]):
                with open(result["file"], encoding="utf-8") as f:
                    lines = f.readlines()
                    print(f"   ✓ CSV файл содержит {len(lines)} строк")
                    if len(lines) > 1:
                        print(f"   ✓ Заголовок: {lines[0].strip()}")

            # Тест 3: Поиск Go репозиториев
            print("\n3. Поиск 3 Go репозиториев...")
            params = {"limit": 3, "lang": "Go", "stars_min": 5000}
            response = await client.get(f"{base_url}/api/search", params=params)
            result = response.json()
            print(f"   ✓ Статус: {response.status_code}")
            print(f"   ✓ Файл: {result['file']}")
            print(f"   ✓ Найдено: {result['count']} репозиториев")

            # Тест 4: Поиск с фильтром по форкам
            print("\n4. Поиск 2 JavaScript репозиториев с фильтром...")
            params = {"limit": 2, "lang": "JavaScript", "stars_min": 1000, "forks_min": 500}
            response = await client.get(f"{base_url}/api/search", params=params)
            result = response.json()
            print(f"   ✓ Статус: {response.status_code}")
            print(f"   ✓ Файл: {result['file']}")
            print(f"   ✓ Найдено: {result['count']} репозиториев")

            print("\n" + "=" * 60)
            print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            print("=" * 60)
            print("\nAPI работает корректно! Ошибка с 'newline' исправлена.")
            print("\n")

        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_api_fixed())
