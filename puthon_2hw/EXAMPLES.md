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
