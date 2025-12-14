# ✅ ПРОБЛЕМА РЕШЕНА - Инструкция по использованию

## Что было исправлено

**Ошибка:** `AIOFile.__init__() got an unexpected keyword argument 'newline'`

**Исправление:** Удален неподдерживаемый параметр `newline=""` из `async_open()` в файле `services/repository_service.py`

## Проверка работы

### ✅ Все тесты пройдены успешно!

Запустите:
```bash
cd C:\Users\User\PycharmProjects\python_phisics\puthon_2hw
python test_api_fixed.py
```

Результат:
```
============================================================
✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!
============================================================

API работает корректно! Ошибка с 'newline' исправлена.
```

## Использование API

### 1. Убедитесь, что сервер запущен

Если сервер не запущен, откройте новое окно PowerShell и выполните:
```bash
cd C:\Users\User\PycharmProjects\python_phisics\puthon_2hw
python run_server.py
```

Вы должны увидеть:
```
Starting server on http://127.0.0.1:8001
INFO:     Started server process
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8001
```

### 2. Примеры запросов

#### Через PowerShell (рекомендуется):

```powershell
# Простой запрос
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Python&stars_min=1000"
Write-Host "Создан файл: $($result.file)"
Write-Host "Найдено: $($result.count) репозиториев"

# Ваш исходный запрос
$result = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=30&lang=JavaScript&stars_min=500&stars_max=2000"
Write-Host "Файл: $($result.file)"

# Просмотр CSV
Get-Content $result.file | Select-Object -First 5
```

#### Через браузер:

1. Откройте: http://127.0.0.1:8001/docs
2. Найдите эндпоинт `/api/search`
3. Нажмите "Try it out"
4. Заполните параметры:
   - limit: 30
   - lang: JavaScript
   - stars_min: 500
   - stars_max: 2000
5. Нажмите "Execute"

#### Через Python:

```python
import httpx
import asyncio

async def search():
    async with httpx.AsyncClient() as client:
        params = {
            "limit": 30,
            "lang": "JavaScript",
            "stars_min": 500,
            "stars_max": 2000
        }
        response = await client.get(
            "http://127.0.0.1:8001/api/search",
            params=params
        )
        result = response.json()
        print(f"Файл: {result['file']}")
        print(f"Найдено: {result['count']} репозиториев")

asyncio.run(search())
```

## CSV файлы

Все CSV файлы сохраняются в папку:
```
C:\Users\User\PycharmProjects\python_phisics\puthon_2hw\static\
```

Формат имени файла:
```
repositories_{язык}_{limit}_{offset}.csv
```

Примеры:
- `repositories_Python_10_0.csv`
- `repositories_JavaScript_30_0.csv`
- `repositories_Go_5_0.csv`

## Структура CSV

```csv
name,owner,stars,forks,language,url,description,created_at,updated_at
"awesome-python","vinta","273695","26897","Python","https://github.com/vinta/awesome-python","An opinionated list...","2014-06-27T21:00:06Z","2025-12-14T10:49:33Z"
```

## Доступные параметры

| Параметр | Тип | Описание | Обязательный | По умолчанию |
|----------|-----|----------|--------------|--------------|
| `limit` | int | Количество репозиториев (1-1000) | ✅ Да | - |
| `offset` | int | Смещение для пагинации | ❌ Нет | 0 |
| `lang` | str | Язык программирования | ❌ Нет | все языки |
| `stars_min` | int | Минимум звезд | ❌ Нет | 0 |
| `stars_max` | int | Максимум звезд | ❌ Нет | без ограничений |
| `forks_min` | int | Минимум форков | ❌ Нет | 0 |
| `forks_max` | int | Максимум форков | ❌ Нет | без ограничений |

## Примеры запросов с разными фильтрами

```powershell
# Python репозитории с > 10000 звезд
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=20&lang=Python&stars_min=10000"

# JavaScript с 1000-5000 звезд
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=15&lang=JavaScript&stars_min=1000&stars_max=5000"

# Go репозитории с > 100 форков
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Go&forks_min=100"

# Любой язык с фильтрами
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=25&stars_min=50000"

# С пагинацией
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=0"  # Страница 1
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=10" # Страница 2
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=20" # Страница 3
```

## Если сервер не отвечает

1. Убедитесь, что сервер запущен (см. раздел "Убедитесь, что сервер запущен")
2. Проверьте, что порт 8001 не занят другим процессом
3. Перезапустите сервер:
   ```powershell
   # Остановить все Python процессы
   taskkill /F /IM python.exe
   
   # Запустить снова
   cd C:\Users\User\PycharmProjects\python_phisics\puthon_2hw
   python run_server.py
   ```

## Полезные ссылки

- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc
- Основная документация: [README.md](README.md)
- Примеры: [EXAMPLES.md](EXAMPLES.md)
- Статус проекта: [STATUS.md](STATUS.md)

---

**✅ Проект полностью работает! Ошибка исправлена!**

