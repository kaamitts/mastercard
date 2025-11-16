# 🏦 Mastercard Analytics Backend

> Natural Language to SQL Analytics API для анализа 11.5 миллионов транзакций Mastercard

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-0.9+-yellow.svg)](https://duckdb.org/)

---

## 📋 СОДЕРЖАНИЕ

- [Обзор](#-обзор)
- [Архитектура](#-архитектура)
- [Как это работает](#-как-это-работает)
- [Структура проекта](#-структура-проекта)
- [Установка](#-установка)
- [Запуск](#-запуск)
- [API Endpoints](#-api-endpoints)
- [Примеры использования](#-примеры-использования)
- [База данных](#-база-данных)
- [Безопасность](#-безопасность)
- [Деплой](#-деплой)
- [Troubleshooting](#-troubleshooting)
- [Для Frontend разработчика](#-для-frontend-разработчика)

---

## 🎯 ОБЗОР

### Что делает этот Backend?

Система принимает **вопросы на естественном языке**, автоматически конвертирует их в **SQL запросы** через NLP модель, выполняет на базе данных с **11.5 миллионами транзакций** Mastercard и возвращает результаты в JSON формате.

### Ключевые возможности
```
✅ Natural Language → SQL (через NLP модель)
✅ 11.5M транзакций в DuckDB
✅ REST API (FastAPI)
✅ Валидация и безопасность SQL
✅ Real-time query execution
✅ Swagger UI документация
✅ CORS поддержка
✅ Логирование запросов
```

### Основной Flow
```
┌─────────────────┐
│  User Question  │  "Top 5 merchants in Kazakhstan"
└────────┬────────┘
         ↓
┌─────────────────┐
│  Backend API    │  POST /ask
│   (FastAPI)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│   NLP Model     │  Gradio @ HuggingFace
│  (Nuraly Team)  │  https://nuraly17-futbolchik.hf.space
└────────┬────────┘
         ↓
    Generated SQL
         ↓
┌─────────────────┐
│  SQL Validator  │  Security checks
└────────┬────────┘
         ↓
┌─────────────────┐
│     DuckDB      │  Execute on 11.5M rows
│  (mastercard.db)│
└────────┬────────┘
         ↓
┌─────────────────┐
│ JSON Response   │  {"success": true, "results": [...]}
└─────────────────┘
```

---

## 🏗️ АРХИТЕКТУРА

### High-Level Architecture
```
┌───────────────────────────────────────────────────────────────┐
│                         FRONTEND                               │
│              (React/Vue/любой клиент)                          │
└───────────────────────────┬───────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                      BACKEND API                               │
│                      (FastAPI)                                 │
│                                                                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   main.py   │  │  models.py   │  │  config.py   │         │
│  │  (Routes)   │  │ (Validation) │  │  (Settings)  │         │
│  └──────┬──────┘  └──────────────┘  └──────────────┘         │
│         │                                                      │
│         ├──────────────┬───────────────┬──────────────┐       │
│         ▼              ▼               ▼              ▼       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐│
│  │nlp_client  │ │validators  │ │  database  │ │   logger   ││
│  │   .py      │ │   .py      │ │    .py     │ │    .py     ││
│  └─────┬──────┘ └────────────┘ └─────┬──────┘ └────────────┘│
└────────┼─────────────────────────────┼────────────────────────┘
         │                              │
         │                              │
         ▼                              ▼
┌────────────────┐            ┌──────────────────┐
│   NLP Model    │            │     DuckDB       │
│  (HuggingFace) │            │  (mastercard.db) │
│                │            │                  │
│  Gradio Space  │            │  11.5M rows      │
│  Question→SQL  │            │  SQL Execution   │
└────────────────┘            └──────────────────┘
```

### Компоненты системы

| Компонент | Технология | Назначение |
|-----------|-----------|-----------|
| **API Server** | FastAPI | REST API endpoints, routing |
| **NLP Client** | Gradio Client | Подключение к NLP модели |
| **Database** | DuckDB | Аналитическая БД, SQL execution |
| **Validators** | Python | SQL security, санитизация |
| **Models** | Pydantic | Data validation, schemas |
| **Logger** | Python logging | Логирование запросов |
| **Config** | Pydantic Settings | Конфигурация, .env |

---

## ⚙️ КАК ЭТО РАБОТАЕТ

### Детальный Flow обработки запроса
```
1️⃣ REQUEST RECEIVED
   Frontend → POST /ask {"query": "Top 5 merchants"}
   ↓
   main.py получает запрос
   ↓ QueryRequest (Pydantic validation)
   
2️⃣ NLP GENERATION
   nlp_client.generate_sql(query)
   ↓
   Gradio API call → https://nuraly17-futbolchik.hf.space
   ↓
   Conversation history передаётся для контекста
   ↓
   NLP модель генерирует SQL
   ↓
   Response: "SELECT merchant_id, SUM(amount)..."
   ⏱️ Time: 20-90 секунд
   
3️⃣ SQL SANITIZATION
   validators.sanitize_sql(sql)
   ↓
   Удаляет артефакты ([/SYS], [/INST], комментарии)
   ↓
   Нормализует пробелы
   ↓
   Clean SQL: "SELECT merchant_id, SUM(transaction_amount_kzt)..."
   
4️⃣ SECURITY VALIDATION
   validators.validate_sql_security(sql)
   ↓
   ✅ Проверка: Только SELECT?
   ✅ Проверка: Нет DROP/DELETE/UPDATE?
   ✅ Проверка: Нет SQL injection паттернов?
   ✅ Проверка: Нет комментариев (--, /**/)?
   ✅ Проверка: Использует example_dataset?
   ↓
   Если ❌ → HTTPException 400
   
5️⃣ DATABASE EXECUTION
   database.execute_sql(sql)
   ↓
   DuckDB открывает mastercard.db
   ↓
   SQL выполняется на 11,536,850 строк
   ↓
   Results конвертируются в List[Dict]
   ↓
   Применяется LIMIT (max 10,000 rows)
   ⏱️ Time: 0.1-2 секунды
   
6️⃣ RESPONSE FORMATTING
   QueryResponse (Pydantic model)
   ↓
   {
     "success": true,
     "sql": "SELECT...",
     "results": [{...}, {...}],
     "columns": ["merchant_id", "revenue"],
     "count": 5,
     "execution_time": 25.3,
     "error": null
   }
   
7️⃣ LOGGING
   database.log_query(...)
   ↓
   Сохраняется в query_logs таблицу:
   - timestamp
   - user_query
   - generated_sql
   - success/error
   - execution_time
   - rows_returned
```

### Временные характеристики
```
┌─────────────────────────┬──────────────┐
│ Этап                    │ Время        │
├─────────────────────────┼──────────────┤
│ Request validation      │ <0.01s       │
│ NLP generation          │ 20-90s       │
│ SQL sanitization        │ <0.01s       │
│ Security validation     │ <0.01s       │
│ Database execution      │ 0.1-2s       │
│ Response formatting     │ <0.01s       │
│ Logging                 │ <0.01s       │
├─────────────────────────┼──────────────┤
│ TOTAL                   │ 20-90s       │
└─────────────────────────┴──────────────┘

⚠️ Основное время: NLP модель (20-90 сек)
✅ SQL выполнение: Очень быстро (<2 сек)
```

---

## 📁 СТРУКТУРА ПРОЕКТА

### Дерево файлов
```
mastercard-backend/
│
├── 📄 main.py                    # FastAPI приложение (главный файл)
│   ├── Endpoints: /ask, /health, /examples, /schema, /logs
│   ├── CORS middleware
│   ├── Startup/shutdown events
│   └── Error handling
│
├── 📄 database.py                # DuckDB + работа с данными
│   ├── Database class
│   ├── load_parquet() - загрузка данных
│   ├── execute_sql() - выполнение запросов
│   ├── get_schema() - структура таблицы
│   ├── log_query() - сохранение логов
│   └── get_logs() - история запросов
│
├── 📄 nlp_client.py              # Клиент для NLP модели
│   ├── NLPClient class
│   ├── generate_sql() - генерация SQL
│   ├── _extract_sql() - парсинг ответа
│   ├── conversation_history - контекст
│   └── health_check() - проверка доступности
│
├── 📄 models.py                  # Pydantic модели
│   ├── QueryRequest - запрос от Frontend
│   ├── QueryResponse - ответ с результатами
│   ├── HealthResponse - статус системы
│   ├── ExamplesResponse - примеры запросов
│   └── SchemaResponse - схема БД
│
├── 📄 validators.py              # SQL валидация
│   ├── validate_sql_security() - проверка безопасности
│   ├── validate_sql_structure() - проверка структуры
│   └── sanitize_sql() - очистка SQL
│
├── 📄 config.py                  # Настройки
│   ├── Settings class (Pydantic)
│   ├── Переменные окружения (.env)
│   └── Defaults values
│
├── 📄 logger.py                  # Логирование
│   ├── File handler (logs/backend.log)
│   ├── Console handler (stdout)
│   ├── log_query() - логи запросов
│   └── log_nlp_call() - логи NLP вызовов
│
├── 📄 requirements.txt           # Python зависимости
│   ├── fastapi==0.104.1
│   ├── duckdb==0.9.2
│   ├── gradio_client==0.7.3
│   └── ... (всего 9 пакетов)
│
├── 📄 .env                       # Переменные окружения (НЕ коммитится!)
│   ├── NLP_MODEL_URL
│   ├── DATABASE_PATH
│   ├── CORS_ORIGINS
│   └── LOG_LEVEL
│
├── 📄 .env.example               # Пример .env (коммитится)
│
├── 📄 .gitignore                 # Git ignore
│   ├── Игнорирует: *.db, *.parquet, .env, logs/
│   └── Коммитится только код
│
├── 📄 README.md                  # Документация (этот файл!)
│
├── 📁 data/                      # Папка с данными
│   ├── dataset.parquet           # Исходные данные (600 MB)
│   └── .gitkeep                  # Держит пустую папку в Git
│
├── 📁 logs/                      # Папка с логами
│   ├── backend.log               # Файл логов
│   └── .gitkeep
│
└── 💾 mastercard.db              # DuckDB база (создаётся автоматически)
    └── mastercard.db.wal         # Write-Ahead Log (временный файл)
```

### Описание каждого файла

#### **main.py** (180 строк)

Главный файл приложения FastAPI.

**Что делает:**
- Создаёт FastAPI app
- Регистрирует endpoints
- Настраивает CORS
- Обрабатывает startup/shutdown events
- Координирует все компоненты

**Ключевые функции:**
```python
@app.post("/ask") - Главный endpoint (NL → SQL → Results)
@app.get("/health") - Health check
@app.get("/examples") - Примеры запросов
@app.get("/schema") - Схема БД
@app.get("/logs") - История запросов
```

---

#### **database.py** (200 строк)

Работа с DuckDB базой данных.

**Что делает:**
- Подключение к DuckDB
- Загрузка Parquet → DuckDB
- Выполнение SQL запросов
- Конвертация результатов в JSON
- Логирование в БД

**Ключевые функции:**
```python
load_parquet() - Загрузить данные из Parquet
execute_sql() - Выполнить SQL запрос
get_schema() - Получить структуру таблицы
get_row_count() - Количество строк
log_query() - Сохранить запрос в лог
get_logs() - Получить историю
```

---

#### **nlp_client.py** (120 строк)

Интеграция с NLP моделью на HuggingFace.

**Что делает:**
- Подключается к Gradio Space
- Отправляет вопрос в модель
- Получает SQL в ответе
- Парсит и очищает SQL
- Управляет conversation history

**Ключевые функции:**
```python
generate_sql(query) - Генерировать SQL
_extract_sql(response) - Извлечь SQL из ответа
clear_history() - Очистить историю
health_check() - Проверить доступность
```

**API модели:**
```
URL: https://nuraly17-futbolchik.hf.space
Method: Gradio Client
Endpoint: /handle_submit
Input: (query, conversation_history)
Output: (query, updated_conversation)
```

---

#### **validators.py** (100 строк)

Валидация и безопасность SQL запросов.

**Что делает:**
- Проверяет безопасность SQL
- Блокирует опасные команды
- Обнаруживает SQL injection
- Санитизирует SQL
- Проверяет структуру

**Ключевые функции:**
```python
validate_sql_security(sql) - Безопасность
validate_sql_structure(sql) - Структура
sanitize_sql(sql) - Очистка
```

**Что блокируется:**
```sql
❌ DROP, DELETE, UPDATE, INSERT
❌ Комментарии (-- , /**/)
❌ Множественные запросы (;)
❌ SQL injection паттерны
❌ Неправильная таблица
```

---

#### **models.py** (80 строк)

Pydantic модели для валидации данных.

**Модели:**
```python
QueryRequest - Запрос от Frontend
  ├── query: str

QueryResponse - Ответ с результатами
  ├── success: bool
  ├── sql: str
  ├── results: List[Dict]
  ├── columns: List[str]
  ├── count: int
  ├── execution_time: float
  └── error: Optional[str]

HealthResponse - Статус системы
SchemaResponse - Схема БД
ExamplesResponse - Примеры
LogEntry - Запись лога
```

---

#### **config.py** (40 строк)

Конфигурация приложения.

**Settings:**
```python
# NLP Model
nlp_model_url: str
nlp_timeout: int

# Database
database_path: str
dataset_path: str
table_name: str

# CORS
cors_origins: List[str]

# Limits
max_results: int
query_timeout: int

# Logging
log_level: str
log_file: str
```

---

#### **logger.py** (50 строк)

Настройка логирования.

**Handlers:**
- File handler → `logs/backend.log`
- Console handler → stdout

**Functions:**
```python
log_query() - Логировать запрос
log_nlp_call() - Логировать NLP вызов
log_db_query() - Логировать SQL
```

---

### Размеры файлов
```
Code files:                ~1 KB each
Total Python code:         ~10 KB

data/dataset.parquet:      600 MB
mastercard.db:             ~800 MB
logs/backend.log:          ~5 MB (растёт)

TOTAL REPOSITORY:          ~1.4 GB
```

---

## 🚀 УСТАНОВКА

### Системные требования
```
Python: 3.10 или выше
RAM: 2 GB минимум (рекомендуется 4 GB)
Disk: 2 GB свободного места
OS: Windows / Linux / macOS
```

### Шаг 1: Клонирование репозитория
```bash
git clone <repository-url>
cd mastercard-backend
```

### Шаг 2: Создание виртуального окружения
```bash
# Создать venv
python -m venv venv

# Активировать
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Шаг 3: Установка зависимостей
```bash
pip install -r requirements.txt
```

**Устанавливается:**
```
fastapi==0.104.1        # API framework
uvicorn[standard]==0.24.0  # ASGI server
duckdb==0.9.2          # Database
pydantic==2.5.0        # Data validation
pydantic-settings==2.1.0  # Settings management
python-dotenv==1.0.0   # .env support
requests==2.31.0       # HTTP client
python-multipart==0.0.6  # Form data
gradio_client==0.7.3   # NLP model client
```

### Шаг 4: Настройка .env
```bash
# Копировать пример
cp .env.example .env

# Отредактировать .env (опционально)
nano .env
```

**Пример .env:**
```env
# NLP Model
NLP_MODEL_URL=https://nuraly17-futbolchik.hf.space

# Database
DATABASE_PATH=mastercard.db
DATASET_PATH=data/dataset.parquet
TABLE_NAME=example_dataset

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/backend.log
```

### Шаг 5: Получить dataset.parquet

**⚠️ Важно:** Файл `dataset.parquet` (600 MB) не хранится в Git!

**Получите от команды:**
- Google Drive link
- Dropbox link
- Или другой источник

**Положите в:**
```bash
data/dataset.parquet
```

### Шаг 6: Загрузить данные в DuckDB
```bash
python -c "from database import db; db.load_parquet()"
```

**Ожидаемый вывод:**
```
INFO:mastercard_backend:✅ DuckDB connected: mastercard.db
INFO:mastercard_backend:📊 Loading dataset from data/dataset.parquet...
INFO:mastercard_backend:✅ Loaded 11,536,850 rows into 'example_dataset'
INFO:mastercard_backend:📋 Table 'example_dataset' schema:
INFO:mastercard_backend:   transaction_id               VARCHAR
INFO:mastercard_backend:   transaction_timestamp        TIMESTAMP
...
```

**Создаётся файл:**
```
mastercard.db (~800 MB)
```

---

## ▶️ ЗАПУСК

### Запуск Backend
```bash
python main.py
```

**Ожидаемый вывод:**
```
INFO:mastercard_backend:✅ DuckDB connected: mastercard.db
INFO:mastercard_backend:🔗 Connecting to NLP model: https://nuraly17-futbolchik.hf.space
Loaded as API: https://nuraly17-futbolchik.hf.space/ ✔
INFO:mastercard_backend:✅ Connected to NLP model
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:mastercard_backend:============================================================
INFO:mastercard_backend:🚀 Starting Mastercard Analytics API v1.0.0
INFO:mastercard_backend:============================================================
INFO:mastercard_backend:✅ Database ready: 11,536,850 rows in example_dataset
INFO:mastercard_backend:✅ NLP model connected: https://nuraly17-futbolchik.hf.space
INFO:mastercard_backend:============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

✅ **Backend работает!**

### Проверка работоспособности

**1. Откройте в браузере:**
```
http://localhost:8000/docs
```

Должна открыться **Swagger UI** с документацией API!

**2. Health check:**
```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "database": "connected",
  "nlp_model": "connected",
  "timestamp": "2025-11-16T06:42:00",
  "version": "1.0.0"
}
```

**3. Тестовый запрос:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "show me top 5 transactions"}'
```

---

## 🔌 API ENDPOINTS

### Полная документация

**Base URL:** `http://localhost:8000`

**Swagger UI:** `http://localhost:8000/docs`

---

### 1. POST /ask

**Описание:** Главный endpoint - принимает вопрос на естественном языке, генерирует SQL, выполняет и возвращает результаты.

**Request:**
```http
POST /ask HTTP/1.1
Content-Type: application/json

{
  "query": "Top 5 merchants by revenue in Kazakhstan"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "sql": "SELECT merchant_id, SUM(transaction_amount_kzt) as revenue FROM example_dataset WHERE acquirer_country_iso='KAZ' GROUP BY merchant_id ORDER BY revenue DESC LIMIT 5",
  "results": [
    {
      "merchant_id": 12345,
      "revenue": 999999.99
    },
    {
      "merchant_id": 67890,
      "revenue": 888888.88
    },
    ...
  ],
  "columns": ["merchant_id", "revenue"],
  "count": 5,
  "execution_time": 25.347,
  "error": null
}
```

**Response (Error - 400):**
```json
{
  "detail": "Only SELECT queries are allowed"
}
```

**Response (Error - 500):**
```json
{
  "detail": "Database error: ..."
}
```

**Response (Error - 503):**
```json
{
  "detail": "NLP model error: ..."
}
```

**Performance:**
```
NLP generation:  20-90 секунд
SQL execution:   0.1-2 секунды
Total:          20-90 секунд
```

---

### 2. GET /health

**Описание:** Проверка работоспособности всех компонентов.

**Request:**
```http
GET /health HTTP/1.1
```

**Response (200):**
```json
{
  "status": "ok",
  "database": "connected",
  "nlp_model": "connected",
  "timestamp": "2025-11-16T06:42:00.123456",
  "version": "1.0.0"
}
```

**Возможные статусы:**
- `status`: `"ok"` или `"degraded"`
- `database`: `"connected"` или `"disconnected"`
- `nlp_model`: `"connected"` или `"disconnected"`

---

### 3. GET /examples

**Описание:** Получить список примеров запросов для тестирования.

**Request:**
```http
GET /examples HTTP/1.1
```

**Response (200):**
```json
{
  "examples": [
    "Top 5 merchants by revenue in Kazakhstan",
    "Total transactions in Almaty in 2024",
    "Average transaction amount by wallet type",
    "Decline rate in October",
    "Transactions above 10000 KZT",
    "Monthly transaction trends",
    "Merchants with most transactions",
    "Count transactions by payment method"
  ]
}
```

---

### 4. GET /schema

**Описание:** Получить структуру таблицы базы данных.

**Request:**
```http
GET /schema HTTP/1.1
```

**Response (200):**
```json
{
  "table": "example_dataset",
  "columns": {
    "transaction_id": "VARCHAR",
    "transaction_timestamp": "TIMESTAMP",
    "card_id": "BIGINT",
    "expiry_date": "VARCHAR",
    "issuer_bank_name": "VARCHAR",
    "merchant_id": "BIGINT",
    "merchant_mcc": "BIGINT",
    "mcc_category": "VARCHAR",
    "merchant_city": "VARCHAR",
    "transaction_type": "VARCHAR",
    "transaction_amount_kzt": "DOUBLE",
    "original_amount": "DOUBLE",
    "transaction_currency": "VARCHAR",
    "acquirer_country_iso": "VARCHAR",
    "pos_entry_mode": "VARCHAR",
    "wallet_type": "VARCHAR"
  },
  "total_rows": 11536850
}
```

---

### 5. GET /logs

**Описание:** Получить последние N запросов (для аудита).

**Request:**
```http
GET /logs?limit=10 HTTP/1.1
```

**Query Parameters:**
- `limit` (optional): Количество записей (default: 50, max: 1000)

**Response (200):**
```json
{
  "count": 10,
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-11-16T06:42:15.123456",
      "user_query": "Top 5 merchants",
      "generated_sql": "SELECT merchant_id, COUNT(*) FROM...",
      "success": true,
      "error_message": null,
      "execution_time": 25.347,
      "rows_returned": 5
    },
    ...
  ]
}
```

---

### 6. POST /clear-history

**Описание:** Очистить conversation history с NLP моделью.

**Request:**
```http
POST /clear-history HTTP/1.1
```

**Response (200):**
```json
{
  "message": "Conversation history cleared"
}
```

**Когда использовать:**
- Начать новую "сессию" вопросов
- Сбросить контекст разговора
- Если модель "запуталась"

---

### 7. GET / (Root)

**Описание:** Корневой endpoint с информацией об API.

**Request:**
```http
GET / HTTP/1.1
```

**Response (200):**
```json
{
  "message": "Welcome to Mastercard Analytics API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 8. GET /docs

**Описание:** Swagger UI - интерактивная документация.

**URL:**
```
http://localhost:8000/docs
```

**Features:**
- Список всех endpoints
- Try it out - тестирование прямо в браузере
- Request/Response примеры
- Schema definitions

---

## 💻 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ

### JavaScript (Vanilla)
```javascript
async function askBackend(query) {
  const API_URL = 'http://localhost:8000';
  
  try {
    const response = await fetch(`${API_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }
    
    const data = await response.json();
    
    if (data.success) {
      console.log('✅ SQL:', data.sql);
      console.log('📊 Results:', data.results);
      console.log('📈 Count:', data.count);
      console.log('⏱️  Time:', data.execution_time);
      return data;
    } else {
      console.error('❌ Error:', data.error);
      throw new Error(data.error);
    }
    
  } catch (error) {
    console.error('💥 Request failed:', error);
    throw error;
  }
}

// Использование
askBackend("Top 5 merchants in Kazakhstan")
  .then(data => {
    // Обработать результаты
    data.results.forEach(row => {
      console.log(row);
    });
  })
  .catch(error => {
    // Показать ошибку пользователю
    alert(`Error: ${error.message}`);
  });
```

---

### React Component (полный пример)
```jsx
import { useState } from 'react';

function AnalyticsChatbot() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const API_URL = 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
        signal: AbortSignal.timeout(120000) // 120 секунд timeout
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Request failed');
      }
      
      const data = await response.json();
      setResults(data);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <h1>🏦 Mastercard Analytics</h1>
      
      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question (e.g., Top 5 merchants)"
          disabled={loading}
          style={{ width: '500px', padding: '10px' }}
        />
        <button type="submit" disabled={loading || !query.trim()}>
          {loading ? '⏳ Processing...' : '🚀 Ask'}
        </button>
      </form>
      
      {/* Loading State */}
      {loading && (
        <div className="loading">
          <p>⏳ Analyzing your question...</p>
          <p style={{ fontSize: '12px', color: '#666' }}>
            This may take 20-90 seconds (NLP model processing)
          </p>
        </div>
      )}
      
      {/* Error State */}
      {error && (
        <div className="error" style={{ color: 'red', padding: '10px', background: '#fee' }}>
          <strong>❌ Error:</strong> {error}
        </div>
      )}
      
      {/* Results */}
      {results && results.success && (
        <div className="results">
          {/* SQL Query */}
          <div style={{ marginTop: '20px' }}>
            <h3>Generated SQL:</h3>
            <pre style={{ background: '#f5f5f5', padding: '10px', overflow: 'auto' }}>
              <code>{results.sql}</code>
            </pre>
          </div>
          
          {/* Results Table */}
          <div style={{ marginTop: '20px' }}>
            <h3>Results ({results.count} rows):</h3>
            <table border="1" cellPadding="8" style={{ borderCollapse: 'collapse', width: '100%' }}>
              <thead>
                <tr style={{ background: '#eee' }}>
                  {results.columns.map(col => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.results.map((row, i) => (
                  <tr key={i}>
                    {results.columns.map(col => (
                      <td key={col}>{JSON.stringify(row[col])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Metadata */}
          <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
            ⏱️ Execution time: {results.execution_time.toFixed(2)}s
          </div>
        </div>
      )}
    </div>
  );
}

export default AnalyticsChatbot;
```

---

### Python (для тестирования)
```python
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_health():
    """Проверить health"""
    response = requests.get(f"{API_URL}/health")
    print("Health:", response.json())

def test_ask(query: str):
    """Протестировать запрос"""
    print(f"\n🔍 Query: {query}")
    
    start = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": query},
            timeout=120  # 120 секунд для NLP
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   SQL: {data['sql']}")
            print(f"   Rows: {data['count']}")
            print(f"   Time: {data['execution_time']:.2f}s (total: {elapsed:.2f}s)")
            
            # Показать первые 3 результата
            for i, row in enumerate(data['results'][:3], 1):
                print(f"   Row {i}: {row}")
                
            return data
        else:
            error = response.json()
            print(f"❌ Error: {error.get('detail')}")
            return None
            
    except requests.Timeout:
        print(f"⏰ Timeout after {elapsed:.2f}s")
        return None
    except Exception as e:
        print(f"💥 Exception: {e}")
        return None

# Тесты
if __name__ == "__main__":
    print("="*60)
    print("🧪 ТЕСТИРОВАНИЕ BACKEND API")
    print("="*60)
    
    # Health check
    test_health()
    
    # Test queries
    queries = [
        "show me top 5 transactions",
        "Top 5 merchants by revenue",
        "Total transactions in Almaty",
        "Average transaction amount"
    ]
    
    for query in queries:
        test_ask(query)
        time.sleep(2)  # Пауза между запросами
    
    print("\n" + "="*60)
    print("✅ Тесты завершены")
    print("="*60)
```

---

### cURL примеры
```bash
# Health check
curl http://localhost:8000/health

# Get examples
curl http://localhost:8000/examples

# Get schema
curl http://localhost:8000/schema

# Ask question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "show me top 5 transactions by amount"}'

# Get logs
curl http://localhost:8000/logs?limit=10

# Clear history
curl -X POST http://localhost:8000/clear-history
```

---

## 💾 БАЗА ДАННЫХ

### Структура хранения
```
data/dataset.parquet           # Исходный файл
    ↓
    Размер: 600 MB
    Формат: Apache Parquet (колоночное хранение)
    Строк: 11,536,850
    Компрессия: Snappy
    ↓
    load_parquet()
    ↓
mastercard.db                  # Рабочая база DuckDB
mastercard.db.wal              # Write-Ahead Log (временный)
    ↓
    Размер: ~800 MB + 5-50 MB
    Формат: DuckDB database file
    Таблицы: 
      - example_dataset (11.5M строк)
      - query_logs (история запросов)
```

### Таблица: example_dataset

**Схема:**

| Колонка | Тип | Описание | Пример |
|---------|-----|----------|--------|
| transaction_id | VARCHAR | Уникальный ID транзакции | "TXN_123456789" |
| transaction_timestamp | TIMESTAMP | Дата и время | 2024-10-15 14:30:25 |
| card_id | BIGINT | ID карты | 1234567890123456 |
| expiry_date | VARCHAR | Срок действия | "12/25" |
| issuer_bank_name | VARCHAR | Банк-эмитент | "Kaspi Bank" |
| merchant_id | BIGINT | ID мерчанта | 98765 |
| merchant_mcc | BIGINT | MCC код | 5411 |
| mcc_category | VARCHAR | Категория | "Grocery Stores" |
| merchant_city | VARCHAR | Город мерчанта | "Almaty" |
| transaction_type | VARCHAR | Тип транзакции | "POS" |
| transaction_amount_kzt | DOUBLE | Сумма в тенге | 15000.50 |
| original_amount | DOUBLE | Оригинальная сумма | 15000.50 |
| transaction_currency | VARCHAR | Валюта | "KZT" |
| acquirer_country_iso | VARCHAR | Код страны | "KAZ" |
| pos_entry_mode | VARCHAR | Способ ввода | "Chip" |
| wallet_type | VARCHAR | Тип кошелька | "Apple Pay" |

**Статистика:**
```sql
SELECT 
  COUNT(*) as total_transactions,
  COUNT(DISTINCT merchant_id) as unique_merchants,
  COUNT(DISTINCT merchant_city) as unique_cities,
  MIN(transaction_timestamp) as earliest_date,
  MAX(transaction_timestamp) as latest_date,
  SUM(transaction_amount_kzt) as total_volume_kzt,
  AVG(transaction_amount_kzt) as avg_transaction_kzt
FROM example_dataset;
```

---

### Таблица: query_logs

**Схема:**

| Колонка | Тип | Описание |
|---------|-----|----------|
| id | INTEGER | Auto-increment ID |
| timestamp | TIMESTAMP | Время запроса |
| user_query | TEXT | Вопрос пользователя |
| generated_sql | TEXT | Сгенерированный SQL |
| success | BOOLEAN | Успех/ошибка |
| error_message | TEXT | Текст ошибки |
| execution_time | FLOAT | Время выполнения (сек) |
| rows_returned | INTEGER | Количество строк |

**Примеры запросов:**
```sql
-- Последние 10 запросов
SELECT * FROM query_logs 
ORDER BY timestamp DESC 
LIMIT 10;

-- Статистика успешности
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
  AVG(execution_time) as avg_time
FROM query_logs;

-- Самые популярные запросы
SELECT user_query, COUNT(*) as count
FROM query_logs
GROUP BY user_query
ORDER BY count DESC
LIMIT 10;
```

---

### DuckDB особенности

**Что такое DuckDB?**

DuckDB - это **встроенная аналитическая СУБД** (embedded OLAP database).

**Аналогия:**
- SQLite - для транзакций (OLTP)
- DuckDB - для аналитики (OLAP)

**Преимущества:**
```
✅ Встроенная (no server needed)
✅ Один файл = вся база
✅ Колоночное хранение (fast aggregations)
✅ Векторизованные операции (SIMD)
✅ Поддержка 100M+ строк
✅ Читает Parquet напрямую
✅ Совместима с pandas/arrow
✅ SQL совместимость (PostgreSQL-like)
```

**Производительность:**
```
Simple SELECT:           0.01-0.1s
Aggregation (GROUP BY):  0.1-1s
Complex JOIN:            1-5s
Full table scan:         2-10s
```

**Write-Ahead Log (.wal файл):**
```
Что это?
  Временный файл для записи изменений

Зачем?
  ✅ Быстрее записывает
  ✅ Защита от потери данных
  ✅ Concurrent reads

Можно удалить?
  ⚠️ НЕТ, пока БД открыта
  ✅ ДА, когда БД закрыта (пересоздастся)

Коммитить в Git?
  ❌ НЕТ (автоматически создаётся)
```

---

### Команды для работы с БД

**Пересоздать базу:**
```bash
# Удалить старую
rm mastercard.db mastercard.db.wal

# Создать заново из parquet
python -c "from database import db; db.load_parquet()"
```

**Посмотреть схему:**
```python
from database import db
schema = db.get_schema()
for col, dtype in schema.items():
    print(f"{col:30s} {dtype}")
```

**Посмотреть статистику:**
```python
from database import db
count = db.get_row_count()
print(f"Total rows: {count:,}")
```

**Выполнить свой SQL:**
```python
from database import db
results = db.execute_sql("SELECT merchant_city, COUNT(*) FROM example_dataset GROUP BY merchant_city LIMIT 10")
for row in results:
    print(row)
```

**Посмотреть логи:**
```python
from database import db
logs = db.get_logs(limit=10)
for log in logs:
    print(f"{log['timestamp']}: {log['user_query']} - {log['success']}")
```

---

## 🔒 БЕЗОПАСНОСТЬ

### SQL Injection Protection

Все SQL запросы проходят **валидацию** перед выполнением.

**Этапы валидации:**
```
1. Sanitization (validators.sanitize_sql)
   ↓
   Удаляет артефакты: [/SYS], [/INST], лишние пробелы
   
2. Security Check (validators.validate_sql_security)
   ↓
   ✅ Только SELECT?
   ✅ Нет DROP/DELETE/UPDATE/INSERT?
   ✅ Нет опасных команд (EXEC, GRANT, etc.)?
   ✅ Нет SQL injection паттернов?
   ✅ Нет комментариев (-- , /**/)?
   
3. Structure Check (validators.validate_sql_structure)
   ↓
   ✅ Использует example_dataset?
   ✅ Правильный формат?
   
4. Execution (database.execute_sql)
   ↓
   Если всё ОК → выполняет SQL
   Если НЕ ОК → HTTPException 400
```

**Что разрешено:**
```sql
✅ SELECT
✅ WHERE, GROUP BY, ORDER BY, HAVING
✅ JOIN (INNER, LEFT, RIGHT, FULL)
✅ Агрегации: SUM, COUNT, AVG, MAX, MIN
✅ LIMIT, OFFSET
✅ Подзапросы (subqueries)
✅ DISTINCT
✅ CASE WHEN
✅ Функции: CAST, COALESCE, DATE functions
```

**Что запрещено:**
```sql
❌ DROP TABLE/DATABASE
❌ DELETE
❌ UPDATE
❌ INSERT
❌ TRUNCATE
❌ ALTER
❌ CREATE
❌ EXEC/EXECUTE
❌ GRANT/REVOKE
❌ Комментарии: -- , /**/
❌ Множественные запросы: ; SELECT
❌ Неправильная таблица (не example_dataset)
```

**Примеры блокировки:**
```python
# ❌ Блокируется
"DROP TABLE example_dataset;"
→ Error: "Dangerous SQL command detected: DROP"

# ❌ Блокируется
"SELECT * FROM example_dataset; DELETE FROM example_dataset;"
→ Error: "Multiple statements not allowed"

# ❌ Блокируется
"SELECT * FROM example_dataset -- comment"
→ Error: "SQL comments not allowed"

# ❌ Блокируется
"SELECT * FROM users WHERE id=1 OR 1=1"
→ Error: "Query must use 'example_dataset' table"

# ✅ Разрешается
"SELECT merchant_city, COUNT(*) FROM example_dataset GROUP BY merchant_city"
→ OK
```

---

### CORS Configuration

**Что такое CORS?**

Cross-Origin Resource Sharing - механизм безопасности браузера.

**Зачем нужен?**

Разрешает Frontend (localhost:3000) обращаться к Backend (localhost:8000).

**Настройка (.env):**
```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","https://your-frontend.com"]
```

**В коде (main.py):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Откуда разрешены запросы
    allow_credentials=True,               # Cookies разрешены
    allow_methods=["*"],                  # Все HTTP методы
    allow_headers=["*"],                  # Все headers
)
```

**Добавить новый origin:**

1. Отредактируйте `.env`:
```env
CORS_ORIGINS=["http://localhost:3000","https://new-frontend.com"]
```

2. Перезапустите Backend

---

### Rate Limiting (TODO)

**Пока НЕ реализовано!**

Для продакшена рекомендуется добавить:
```bash
pip install slowapi
```
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/ask")
@limiter.limit("10/minute")  # 10 запросов в минуту
async def ask(...):
    ...
```

---

### Логирование для аудита

Все запросы логируются в:

**1. Файл логов:**
```
logs/backend.log
```

**2. База данных:**
```sql
SELECT * FROM query_logs;
```

**Что логируется:**
- Timestamp
- User query (вопрос пользователя)
- Generated SQL
- Success/error status
- Error message (если есть)
- Execution time
- Rows returned

**Просмотр логов:**
```bash
# Последние 50 строк
tail -n 50 logs/backend.log

# Real-time мониторинг
tail -f logs/backend.log
```

---

## 🌐 ДЕПЛОЙ

### Локальный запуск (для разработки/демо)

**Если Backend и Frontend на ОДНОМ компьютере:**
```bash
# Терминал 1 - Backend
cd mastercard-backend
python main.py
# Работает на localhost:8000

# Терминал 2 - Frontend
cd frontend
npm start
# Работает на localhost:3000
# Обращается к http://localhost:8000
```

✅ **Никакой дополнительный setup не нужен!**

---

### Деплой с ngrok (если на разных компьютерах)

**Когда нужен ngrok:**
- Backend на вашем компе
- Frontend на компе коллеги
- Вы в разных местах/сетях

**Установка ngrok:**

1. Скачайте: https://ngrok.com/download
2. Распакуйте `ngrok.exe`
3. (Опционально) Зарегистрируйтесь на ngrok.com для постоянного URL

**Запуск:**
```bash
# Терминал 1 - Backend
python main.py

# Терминал 2 - ngrok
ngrok http 8000
```

**Вывод ngrok:**
```
Session Status                online
Forwarding                    https://abc123-xyz.ngrok-free.app -> http://localhost:8000
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                              ВАШ ПУБЛИЧНЫЙ URL
```

**Добавьте в CORS (.env):**
```env
CORS_ORIGINS=["http://localhost:3000","https://abc123-xyz.ngrok-free.app"]
```

**Перезапустите Backend**

**Отправьте Frontend команде:**
```
Backend URL: https://abc123-xyz.ngrok-free.app

Endpoints:
- POST https://abc123-xyz.ngrok-free.app/ask
- GET https://abc123-xyz.ngrok-free.app/docs
```

**⚠️ Важно:**
- Бесплатный ngrok: URL меняется при каждом перезапуске
- Оба терминала должны работать (backend + ngrok)
- Есть лимиты на количество запросов

---

### Деплой на сервер (Production)

**Рекомендуемые платформы:**

#### **1. Render.com** (бесплатно, рекомендуется)
```yaml
# render.yaml
services:
  - type: web
    name: mastercard-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.10
```

**Процесс:**
1. Пуш код в GitHub
2. Создать New Web Service на render.com
3. Подключить GitHub репо
4. Deploy!

**URL:** `https://your-app.onrender.com`

---

#### **2. Railway.app** (бесплатно, простой)
```bash
# Установить Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**URL:** `https://your-app.railway.app`

---

#### **3. Fly.io** (бесплатно, быстрый)
```dockerfile
# Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```
```bash
# Deploy
fly launch
fly deploy
```

---

### ⚠️ Проблемы с деплоем

**Проблема: dataset.parquet слишком большой (600 MB)**

**Решение 1:** Не коммитить в Git, загружать отдельно
```bash
# .gitignore
data/*.parquet

# На сервере:
wget https://your-cloud-storage.com/dataset.parquet -O data/dataset.parquet
python -c "from database import db; db.load_parquet()"
```

**Решение 2:** Использовать cloud storage
```python
# Загрузка из S3/Google Cloud
import boto3
s3.download_file('bucket', 'dataset.parquet', 'data/dataset.parquet')
```

**Решение 3:** Использовать готовую БД
```bash
# Создать mastercard.db локально
# Загрузить mastercard.db на сервер
# Не нужен dataset.parquet на сервере!
```

---

## 🐛 TROUBLESHOOTING

### Проблема: "Cannot open file mastercard.db - file busy"

**Причина:**

База уже открыта другим процессом (обычно из-за `reload=True` в uvicorn).

**Решение:**
```python
# main.py - измените reload на False
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    reload=False,  # ← ИЗМЕНИТЬ
    log_level="info"
)
```

Или запустите без reload:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

### Проблема: "NLP model timeout" или долгие запросы

**Причина:**

NLP модель занимает 20-90 секунд для генерации SQL.

**Это нормально!** Бесплатная модель на HuggingFace.

**Решения:**

**1. Увеличьте timeout в .env:**
```env
NLP_TIMEOUT=120
```

**2. В Frontend увеличьте timeout:**
```javascript
fetch(url, { 
    signal: AbortSignal.timeout(120000)  // 120 секунд
})
```

**3. Показывайте loading indicator:**
```jsx
{loading && <p>⏳ Processing... (20-90 seconds)</p>}
```

**4. Добавьте прогресс:**
```jsx
{loading && (
  <div>
    <p>Analyzing your question...</p>
    <div className="spinner"></div>
    <p>This may take up to 90 seconds</p>
  </div>
)}
```

---

### Проблема: "Only SELECT queries allowed"

**Причина:**

NLP модель сгенерировала не-SELECT запрос или комментарий.

**Решение:**

**1. Используйте английский язык:**
```
✅ "Top 5 merchants by revenue"
✅ "Total transactions in Almaty"
❌ "Покажи мне топ 5 мерчантов" (может не понять)
```

**2. Будьте конкретны:**
```
✅ "Top 5 merchants by transaction amount in Kazakhstan"
❌ "Покажи что-нибудь интересное"
```

**3. Проверьте логи:**
```bash
tail -f logs/backend.log
```

Посмотрите что именно сгенерировала модель.

**4. Очистите history:**
```bash
curl -X POST http://localhost:8000/clear-history
```

---

### Проблема: "Database not loaded"

**Причина:**

Данные не загружены в DuckDB.

**Решение:**
```bash
# Проверьте что parquet файл существует
ls data/dataset.parquet

# Загрузите данные
python -c "from database import db; db.load_parquet()"

# Должно создаться
ls mastercard.db  # Должен появиться файл ~800 MB
```

---

### Проблема: "Port 8000 already in use"

**Причина:**

Порт 8000 занят другим приложением.

**Решение 1:** Убейте процесс
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <номер_процесса> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

**Решение 2:** Используйте другой порт
```bash
uvicorn main:app --port 8001
```

Или в `main.py`:
```python
uvicorn.run(..., port=8001)
```

---

### Проблема: Медленные SQL запросы

**Причина:**

Сложный запрос или большой dataset.

**Оптимизация:**

**1. Используйте LIMIT:**
```sql
-- Медленно
SELECT * FROM example_dataset WHERE merchant_city='Almaty'

-- Быстро
SELECT * FROM example_dataset WHERE merchant_city='Almaty' LIMIT 1000
```

**2. Избегайте SELECT *:**
```sql
-- Медленно
SELECT * FROM example_dataset

-- Быстро
SELECT merchant_id, transaction_amount_kzt FROM example_dataset
```

**3. Используйте индексы (если создадите):**
```sql
CREATE INDEX idx_merchant_city ON example_dataset(merchant_city);
```

---

### Проблема: "Module not found" ошибки

**Причина:**

Зависимости не установлены или venv не активирован.

**Решение:**
```bash
# Активируйте venv
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Проверьте
pip list
```

---

### Логи для отладки

**Где искать логи:**
```
1. Консоль (терминал где запущен Backend)
2. logs/backend.log
3. Database: SELECT * FROM query_logs
```

**Посмотреть последние логи:**
```bash
# Windows PowerShell
Get-Content logs/backend.log -Tail 50

# Linux/Mac
tail -n 50 logs/backend.log

# Real-time
tail -f logs/backend.log
```

**Увеличить детализацию:**
```env
# .env
LOG_LEVEL=DEBUG
```

---

## 👨‍💻 ДЛЯ FRONTEND РАЗРАБОТЧИКА

### Quick Start Guide

**1. Получите код:**
```bash
git clone <repository-url>
cd mastercard-backend
```

**2. Получите dataset.parquet (600 MB):**

Спросите у Backend команды ссылку на Google Drive/Dropbox.

Положите в: `data/dataset.parquet`

**3. Setup:**
```bash
# Создать venv
python -m venv venv

# Активировать
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Установить зависимости
pip install -r requirements.txt

# Настроить .env
cp .env.example .env
# Добавьте свой Frontend URL в CORS_ORIGINS

# Загрузить данные
python -c "from database import db; db.load_parquet()"
```

**4. Запустить:**
```bash
python main.py
```

✅ Backend работает на `http://localhost:8000`

**5. Проверить:**

Откройте: `http://localhost:8000/docs`

---

### Интеграция с Frontend

**Base URL:**
```javascript
const API_URL = 'http://localhost:8000';
// Или если через ngrok:
// const API_URL = 'https://abc123.ngrok-free.app';
```

**Main Endpoint:**
```javascript
async function askQuestion(query) {
  const response = await fetch(`${API_URL}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
    signal: AbortSignal.timeout(120000)  // 120 сек timeout
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Использование
const data = await askQuestion("Top 5 merchants in Kazakhstan");
console.log(data.sql);        // SQL запрос
console.log(data.results);    // Массив результатов
console.log(data.count);      // Количество строк
```

**Response format:**
```typescript
interface QueryResponse {
  success: boolean;
  sql: string;
  results: Array<Record<string, any>>;
  columns: string[];
  count: number;
  execution_time: number;
  error: string | null;
}
```

**Error handling:**
```javascript
try {
  const data = await askQuestion(query);
  // Успех - показать результаты
} catch (error) {
  if (error.message === "Only SELECT queries allowed") {
    // Показать: "Вопрос некорректный, попробуйте переформулировать"
  } else if (error.message.includes("timeout")) {
    // Показать: "Запрос занял слишком много времени"
  } else {
    // Показать: "Ошибка: {error.message}"
  }
}
```

---

### Рекомендации UI/UX

**1. Loading State (обязательно!):**
```jsx
{loading && (
  <div>
    <Spinner />
    <p>Analyzing your question...</p>
    <p style={{fontSize: '12px'}}>
      This may take 20-90 seconds
    </p>
  </div>
)}
```

**2. Timeout должен быть 120+ секунд:**
```javascript
fetch(url, {
  signal: AbortSignal.timeout(120000)
})
```

**3. Показывайте SQL запрос:**
```jsx
{data && (
  <div>
    <h3>Generated SQL:</h3>
    <pre><code>{data.sql}</code></pre>
  </div>
)}
```

**4. Используйте примеры:**
```javascript
// Получить примеры от Backend
const response = await fetch(`${API_URL}/examples`);
const { examples } = await response.json();

// Показать как подсказки
{examples.map(ex => (
  <button onClick={() => setQuery(ex)}>{ex}</button>
))}
```

**5. Обработка ошибок:**
```jsx
{error && (
  <Alert variant="error">
    <AlertTitle>Error</AlertTitle>
    <p>{error}</p>
    <button onClick={retry}>Try Again</button>
  </Alert>
)}
```

---

### Примеры хороших вопросов

Рекомендуйте пользователям такие вопросы:
```
✅ "Top 5 merchants by revenue in Kazakhstan"
✅ "Total transactions in Almaty in 2024"
✅ "Average transaction amount by city"
✅ "Transactions above 10000 KZT"
✅ "Count transactions by payment method"
✅ "Monthly transaction trends"
✅ "Merchants with most declined transactions"
```

Избегайте:
```
❌ "Покажи что-нибудь" (слишком расплывчато)
❌ "Что там с данными?" (нет конкретики)
❌ Вопросы на русском (модель хуже понимает)
```

---

### CORS Troubleshooting

Если видите ошибку:
```
Access to fetch at 'http://localhost:8000/ask' from origin 'http://localhost:3000' 
has been blocked by CORS policy
```

**Решение:**

1. Убедитесь что Backend запущен
2. Проверьте `.env` файл Backend:
```env
CORS_ORIGINS=["http://localhost:3000"]
```

3. Перезапустите Backend

---

### Health Check

Рекомендуется проверять health при загрузке app:
```javascript
useEffect(() => {
  fetch(`${API_URL}/health`)
    .then(r => r.json())
    .then(data => {
      if (data.status !== 'ok') {
        console.warn('Backend degraded:', data);
      }
    })
    .catch(err => {
      console.error('Backend unavailable:', err);
      // Показать пользователю что Backend недоступен
    });
}, []);
```

---

## 📊 ПРОИЗВОДИТЕЛЬНОСТЬ

### Метрики

| Операция | Время | Примечание |
|----------|-------|-----------|
| **NLP generation** | 20-90 сек | Зависит от нагрузки на модель |
| **SQL validation** | <0.01 сек | Мгновенно |
| **Simple SELECT** | 0.01-0.1 сек | Прямой SELECT без GROUP BY |
| **Aggregation** | 0.1-1 сек | GROUP BY, COUNT, SUM |
| **Complex JOIN** | 1-5 сек | Несколько таблиц (если будут) |
| **Full table scan** | 2-10 сек | SELECT * без WHERE |
| **Total request** | **20-90 сек** | **В основном NLP** |

### Оптимизация

**Что быстро:**
```sql
✅ SELECT * FROM example_dataset LIMIT 10;                    -- 0.01s
✅ SELECT * FROM example_dataset WHERE merchant_city='Almaty' LIMIT 100;  -- 0.1s
✅ SELECT merchant_id, COUNT(*) FROM example_dataset GROUP BY merchant_id LIMIT 10;  -- 0.5s
```

**Что медленно:**
```sql
⏱️ SELECT * FROM example_dataset;  -- 10s (11.5M строк!)
⏱️ Complex GROUP BY без LIMIT      -- 2-5s
⏱️ Multiple JOINs                  -- 3-7s
```

**Рекомендации:**
- Всегда используйте LIMIT
- Избегайте SELECT * если не нужны все колонки
- Фильтруйте WHERE перед GROUP BY

---

## 🎓 FAQ

**Q: Почему так долго (20-90 сек)?**

A: Основное время - генерация SQL через NLP модель на HuggingFace. Сама база отвечает за <2 сек. Это нормально для бесплатной модели.

---

**Q: Можно ли ускорить?**

A: Для ускорения нужна платная NLP модель или собственный inference server. Для хакатона это нормально.

---

**Q: Почему используется DuckDB а не PostgreSQL/MySQL?**

A: DuckDB специализирована на аналитике (OLAP), работает без сервера, быстрее на агрегациях, отлично читает Parquet.

---

**Q: Что такое .wal файл?**

A: Write-Ahead Log - временный файл для безопасной записи в БД. Создаётся автоматически, не нужно коммитить в Git.

---

**Q: Можно ли использовать русский язык?**

A: Можно, но модель хуже понимает. Рекомендуется английский для лучшей точности.

---

**Q: Сколько памяти нужно?**

A: Минимум 2 GB RAM. Рекомендуется 4 GB для комфортной работы.

---

**Q: Безопасен ли SQL от модели?**

A: Да! Каждый SQL проходит валидацию. Блокируются DROP, DELETE, UPDATE, injection паттерны.

---

**Q: Можно ли добавить свои данные?**

A: Да! Замените `data/dataset.parquet` и перезагрузите: `db.load_parquet()`. Схема должна быть совместима.

---

**Q: Работает ли offline?**

A: База работает offline, но NLP модель требует интернет (HuggingFace API).

---

## 📞 ПОДДЕРЖКА

### Контакты команды

- **Backend:** Kana
- **NLP Model:** Nuraly - https://nuraly17-futbolchik.hf.space
- **Frontend:** Асылхан

### Полезные ссылки

- **API Docs:** http://localhost:8000/docs
- **FastAPI:** https://fastapi.tiangolo.com
- **DuckDB:** https://duckdb.org/docs
- **Pydantic:** https://docs.pydantic.dev
- **Gradio Client:** https://www.gradio.app/docs/python-client

### Репорт багов

Если нашли баг:

1. Проверьте логи: `logs/backend.log`
2. Попробуйте воспроизвести
3. Сохраните query, error message, logs
4. Свяжитесь с командой Backend

---

## ✅ CHECKLIST ДЛЯ ДЕМО
```
☐ Backend запущен (python main.py)
☐ Health check работает (/health → "ok")
☐ NLP модель подключена (nlp_model: "connected")
☐ База загружена (11,536,850 rows)
☐ Swagger UI открывается (/docs)
☐ Тестовый запрос работает (POST /ask)
☐ Frontend подключён к Backend
☐ CORS настроен (frontend URL в .env)
☐ Логи пишутся (logs/backend.log)
☐ ngrok запущен (если нужен remote access)
☐ Примеры запросов подготовлены
☐ Презентация готова
```

---

## 🎉 ГОТОВО!

Backend полностью документирован и готов к использованию!

**Основные endpoints:**
- `POST /ask` - главный (NL → SQL → Results)
- `GET /health` - проверка
- `GET /docs` - документация

**Ключевые файлы:**
- `main.py` - API endpoints
- `database.py` - DuckDB integration
- `nlp_client.py` - NLP model client
- `validators.py` - SQL security

**Для вопросов:** См. раздел [Поддержка](#-поддержка)

---

**Удачи на хакатоне! 🚀**

*Документация обновлена: 16 ноября 2025*
*Версия: 1.0.0*

---

## 📄 LICENSE

MIT License - используйте свободно для образовательных целей.