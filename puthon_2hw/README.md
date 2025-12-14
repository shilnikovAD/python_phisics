# GitHub Repository Search API

FastAPI приложение для поиска репозиториев на GitHub и экспорта результатов в CSV.

## Установка

1. Установите зависимости:
```bash
make install
```

или

```bash
pip install -r requirements.txt
pip install ruff
```

2. (Опционально) Создайте `.env` файл и добавьте GitHub токен для увеличения лимита запросов:
```
GITHUB_TOKEN=your_token_here
```

## Тестирование

Перед запуском рекомендуется запустить тесты:

```bash
python test_project.py
```

или

```bash
make test
```

## Запуск

```bash
python run_server.py
```

или

```bash
make run
```

Приложение будет доступно по адресу: http://127.0.0.1:8001

## API Документация

После запуска приложения документация API доступна по адресу:
- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

Больше примеров использования в файле [EXAMPLES.md](EXAMPLES.md)

## Использование

### Эндпоинт поиска

`GET /api/search`

#### Параметры:

- `limit` (обязательный): Количество репозиториев для возврата (1-1000)
- `offset` (опциональный): Количество репозиториев для пропуска (по умолчанию: 0)
- `lang` (опциональный): Язык программирования
- `stars_min` (опциональный): Минимальное количество звезд (по умолчанию: 0)
- `stars_max` (опциональный): Максимальное количество звезд
- `forks_min` (опциональный): Минимальное количество форков (по умолчанию: 0)
- `forks_max` (опциональный): Максимальное количество форков

#### Пример запроса:

```bash
curl "http://127.0.0.1:8001/api/search?limit=50&offset=0&lang=Python&stars_min=1000"
```

Или через PowerShell:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8001/api/search?limit=50&lang=Python&stars_min=1000"
```

#### Ответ:

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

## Формат CSV

CSV файл содержит следующие поля:
- `name`: Название репозитория
- `owner`: Владелец репозитория
- `stars`: Количество звезд
- `forks`: Количество форков
- `language`: Язык программирования
- `url`: URL репозитория
- `description`: Описание
- `created_at`: Дата создания
- `updated_at`: Дата последнего обновления

## Проверка кода

```bash
make lint-check
```

## Структура проекта

```
puthon_2hw/
├── main.py                      # Основное приложение FastAPI
├── requirements.txt             # Зависимости
├── Makefile                     # Команды для сборки и запуска
├── pyproject.toml              # Конфигурация ruff
├── endpoints/                   # API эндпоинты
│   ├── __init__.py
│   └── search.py               # Эндпоинт поиска
├── services/                    # Бизнес-логика
│   ├── __init__.py
│   └── repository_service.py   # Сервис работы с репозиториями
├── infrastructure/              # Внешние клиенты
│   ├── __init__.py
│   └── github_client.py        # HTTP клиент для GitHub API
└── static/                      # Статические файлы (CSV)
```

## Технологии

- **FastAPI**: Веб-фреймворк
- **httpx**: Асинхронный HTTP-клиент
- **aiofile**: Асинхронная работа с файлами
- **uvicorn**: ASGI сервер
- **ruff**: Линтер и форматтер

