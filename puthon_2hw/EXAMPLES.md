# Примеры использования GitHub Repository Search API

## Запуск сервера

```bash
python run_server.py
```

Сервер будет доступен по адресу: http://127.0.0.1:8001

## Примеры запросов

### 1. Поиск 50 Python репозиториев с более чем 1000 звезд

```bash
curl "http://127.0.0.1:8001/api/search?limit=50&lang=Python&stars_min=1000"
```

### 2. Поиск JavaScript репозиториев с 500-2000 звезд

```bash
curl "http://127.0.0.1:8001/api/search?limit=30&lang=JavaScript&stars_min=500&stars_max=2000"
```

### 3. Поиск Go репозиториев с более чем 100 форков

```bash
curl "http://127.0.0.1:8001/api/search?limit=20&lang=Go&forks_min=100"
```

### 4. Поиск репозиториев с пагинацией (offset)

```bash
# Первая страница
curl "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=0"

# Вторая страница
curl "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=10"

# Третья страница
curl "http://127.0.0.1:8001/api/search?limit=10&lang=Python&offset=20"
```

### 5. Поиск репозиториев на любом языке с фильтрами

```bash
curl "http://127.0.0.1:8001/api/search?limit=25&stars_min=5000&forks_min=1000"
```

## Примеры использования с Python

### Базовый пример

```python
import httpx
import asyncio

async def search_repos():
    async with httpx.AsyncClient() as client:
        params = {
            "limit": 50,
            "lang": "Python",
            "stars_min": 1000
        }
        response = await client.get(
            "http://127.0.0.1:8001/api/search",
            params=params
        )
        result = response.json()
        print(f"Найдено репозиториев: {result['count']}")
        print(f"CSV файл: {result['file']}")

asyncio.run(search_repos())
```

### Пример с обработкой CSV

```python
import httpx
import asyncio
import csv

async def search_and_process():
    async with httpx.AsyncClient() as client:
        # Поиск репозиториев
        params = {
            "limit": 20,
            "lang": "Rust",
            "stars_min": 500
        }
        response = await client.get(
            "http://127.0.0.1:8001/api/search",
            params=params
        )
        result = response.json()
        
        # Чтение CSV файла
        csv_path = result['file']
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                print(f"{row['name']} by {row['owner']}: {row['stars']} ⭐")

asyncio.run(search_and_process())
```

## Примеры с PowerShell

### Базовый запрос

```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=10&lang=Python&stars_min=1000"
Write-Host "Найдено: $($response.count) репозиториев"
Write-Host "Файл: $($response.file)"
```

### Скачивание нескольких страниц

```powershell
$languages = @("Python", "JavaScript", "Go", "Rust")

foreach ($lang in $languages) {
    $params = @{
        limit = 30
        lang = $lang
        stars_min = 1000
    }
    
    $queryString = ($params.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
    $url = "http://127.0.0.1:8001/api/search?$queryString"
    
    $response = Invoke-RestMethod -Uri $url
    Write-Host "$lang : $($response.count) репозиториев -> $($response.file)"
}
```

## Структура ответа API

```json
{
  "status": "success",
  "message": "Repositories exported to CSV",
  "file": "static/repositories_Python_50_0.csv",
  "count": 50,
  "filters": {
    "limit": 50,
    "offset": 0,
    "language": "Python",
    "stars_min": 1000,
    "stars_max": null,
    "forks_min": 0,
    "forks_max": null
  }
}
```

## Структура CSV файла

CSV файл содержит следующие столбцы:

- `name` - Название репозитория
- `owner` - Владелец репозитория
- `stars` - Количество звезд
- `forks` - Количество форков
- `language` - Язык программирования
- `url` - URL репозитория на GitHub
- `description` - Описание репозитория
- `created_at` - Дата создания
- `updated_at` - Дата последнего обновления

## Swagger UI

Интерактивная документация API доступна по адресу:
http://127.0.0.1:8001/docs

Здесь вы можете:
- Просмотреть все доступные эндпоинты
- Протестировать запросы прямо в браузере
- Посмотреть схемы запросов и ответов

## ReDoc

Альтернативная документация доступна по адресу:
http://127.0.0.1:8001/redoc

## Ограничения

1. **GitHub API Rate Limits**: 
   - Без токена: 60 запросов в час
   - С токеном: 5000 запросов в час
   
2. **Максимальное количество результатов за один запрос**: 1000

3. **Максимальное количество результатов на страницу (GitHub API)**: 100

## Использование GitHub Token

Для увеличения лимита запросов создайте файл `.env`:

```
GITHUB_TOKEN=your_github_personal_access_token
```

Токен можно создать на GitHub:
Settings → Developer settings → Personal access tokens → Generate new token

