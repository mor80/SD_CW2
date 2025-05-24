# SD_CW2
Большое ДЗ № 2 по КПО

*(File-Store → File-Analysis → API-Gateway)*  

## 1. Цель работы
Создать распределённую систему, которая:

1. Принимает текстовые файлы (`POST /files`), хранит их и метаданные.  
2. Анализирует загруженные файлы (статистика + детектирование дубликатов).  
3. Предоставляет единый публичный API через Gateway.  

## 2. Архитектура

```mermaid
flowchart LR
    subgraph internal["Docker network"]
        FS(File-Store<br/>:8000)
        AN(File-Analysis<br/>:8001)
    end
    GW(API-Gateway<br/>:8002):::pub
    DB[(PostgreSQL<br/>:5432)]
    Client((User / cURL)):::pub

    Client  -- upload / download -->  GW
    GW      -- proxy -->  FS
    GW      -- proxy -->  AN
    FS      -- asyncpg --> DB
    AN      -- asyncpg --> DB
classDef pub fill:#bee3f8;
````

### Контейнеры

| Сервис        | Образ                      | Порт наружу                     | Ответственность                                    |
| ------------- | -------------------------- | ------------------------------- | -------------------------------------------------- |
| **filestore** | `file-store/Dockerfile`    | `8000` (можно *не* публиковать) | Загрузка / скачивание файлов, метаданные           |
| **analysis**  | `file-analysis/Dockerfile` | `8001` (можно *не* публиковать) | Статистика, SHA-256, Simhash, хранение результатов |
| **gateway**   | `api-gateway/Dockerfile`   | `8002`                          | Единая точка API, CORS, proxy                      |
| **db**        | `postgres:16-alpine`       | — (только сеть docker-compose)  | БД `store` и, при желании, `analysis`              |

## 3. Основные технологии

* **FastAPI** + Uvicorn (async Python 3.11)
* **SQLAlchemy 2** + **asyncpg**
* **simhash** для «почти» дубликатов
* **pydantic-settings** для конфигурации через `.env`
* **Docker Compose** — изолированная сеть микросервисов

## 4. Структура репозитория

```
project-root/
├ api-gateway/
│  ├ app/          # код Gateway
│  ├ Dockerfile
│  └ requirements.txt
├ file-store/
│  ├ app/          # код File-Store
│  ├ Dockerfile
│  └ requirements.txt
├ file-analysis/
│  ├ app/          # код Analysis
│  ├ Dockerfile
│  └ requirements.txt
├ config/          # общие pydantic-конфиги
│  ├ __init__.py
│  ├ base.py
│  └ ...
├ docker-compose.yml
└ .env.example
```

## 5. Конфигурация (`.env`)

```env
APP_ENV=development

# Postgres базовый пользователь (для File-Store)
FILESTORE_DB_NAME=store
FILESTORE_DB_USER=store
FILESTORE_DB_PASSWORD=secret

# Доп. пользователь/БД для анализа (опционально)
ANALYSIS_DB_NAME=analysis
ANALYSIS_DB_USER=analysis
ANALYSIS_DB_PASSWORD=secret

# Адреса сервисов для Gateway
GATEWAY_FILESTORE_BASE_URL=http://filestore:8000
GATEWAY_ANALYSIS_BASE_URL=http://analysis:8001
GATEWAY_PORT=8002
```

## 6. Запуск

```bash
docker compose up -d --build
```

Доступы:

| Endpoint                                                            | Назначение                                            |
| ------------------------------------------------------------------- | ----------------------------------------------------- |
| `POST   http://localhost:8002/files`                                | Загрузить файл (`multipart/form-data`, поле **file**) |
| `GET    http://localhost:8002/files/{file_id}`                      | Скачать файл                                          |
| `POST   http://localhost:8002/analysis/{file_id}?filename=name.txt` | Запустить анализ                                      |
| `GET    http://localhost:8002/analysis/{file_id}`                   | Получить результат                                    |
| `GET    http://localhost:8002/healthz`                              | Проверка живости Gateway                              |
| `http://localhost:8002/docs`                                        | Swagger-UI Gateway                                    |

*(Порты 8000 и 8001 можно **не** публиковать наружу — клиент работает только с Gateway.)*

## 7. Пример использования

```bash
# загрузка
curl -F "file=@report.txt" http://localhost:8002/files

# => {"file_id":"…","size":1234,...}

# анализ
curl -X POST "http://localhost:8002/analysis/<file_id>?filename=report.txt"

# получение статистики
curl http://localhost:8002/analysis/<file_id>
```

## 8. Заключение

Система разделена на понятные сервисы, легко масштабируется
(хранение, вычисления и публичный API независимы), конфигурируется через
единый `.env` и разворачивается одной командой `docker compose up`.

