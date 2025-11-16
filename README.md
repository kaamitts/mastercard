## 🔗 ДЛЯ FRONTEND РАЗРАБОТЧИКА

### Quick Start

1. **Скачай dataset.parquet** (600 MB)
```
   положи его в data/dataset.parquet
```

2. **Установи зависимости:**
```bash
   pip install -r requirements.txt
```

3. **Настрой .env:**
```bash
   # Добавь свой Frontend URL в CORS_ORIGINS
```

4. **Загрузи данные:**
```bash
   python -c "from database import db; db.load_parquet()"
```

5. **Запусти Backend:**
```bash
   python main.py
```

<!-- 6. **Запусти ngrok (для remote access):**
```bash
   ngrok http 8000
``` -->

7. **Используй публичный URL:**
```
   https://abc123.ngrok-free.app
```

### API Endpoints

**Base URL:** `http://localhost:8000`

**Main endpoint:**
```javascript
POST /ask
Body: {"query": "Top 5 merchants"}

Response: {
  "success": true,
  "sql": "SELECT...",
  "results": [...],
  "count": 5,
  "execution_time": 25.3
}
```

**Health check:**
```javascript
GET /health
```

**Documentation:**
```
http://localhost:8000/docs
```