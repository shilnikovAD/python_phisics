# GitHub Repository Search API

FastAPI приложение для поиска репозиториев на GitHub и экспорта результатов в CSV.

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
pip install ruff
```

**Для Windows:** используйте make-скрипты:
```powershell
.\make.ps1 install
# или
.\make.bat install
```

## Тестирование

Перед запуском рекомендуется запустить тесты:

```bash
python test_project.py
```
## Запуск

### PowerShell (Windows)
```powershell
# Из директории puthon_2hw
python run_server.py
```

### Bash/Linux/Mac
```bash
python run_server.py
```

Приложение будет доступно по адресу: **http://127.0.0.1:9000**

## API Документация

После запуска приложения документация API доступна по адресу:
- Swagger UI: http://127.0.0.1:9000/docs
- ReDoc: http://127.0.0.1:9000/redoc

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

#### Примеры запросов:

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:9000/api/search?limit=50&offset=0&lang=Python&stars_min=1000" -UseBasicParsing
```

**Curl (если установлен):**
```bash
curl "http://127.0.0.1:9000/api/search?limit=50&offset=0&lang=Python&stars_min=1000"
```

**Или просто откройте в браузере:**
```
http://127.0.0.1:9000/api/search?limit=50&lang=Python&stars_min=1000
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

**Вариант 1: Через make-скрипты (Windows):**
```powershell
.\make.ps1 lint-check
# или
.\make.bat lint-check
```

**Вариант 2: Напрямую (все платформы):**
```bash
python -m ruff check . --fix
python -m ruff format . --check
```

**Вариант 3: Linux/Mac с установленным make:**
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

