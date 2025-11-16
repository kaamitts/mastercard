"""
FastAPI Backend для Mastercard Analytics
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import time

from config import settings
from logger import logger
from models import (
    QueryRequest, QueryResponse, HealthResponse,
    ExamplesResponse, SchemaResponse
)
from database import db
from nlp_client import nlp_client
from validators import validate_sql_security, validate_sql_structure, sanitize_sql

# ============================================
# СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ============================================

app = FastAPI(
    title=settings.app_name,
    description="Natural Language to SQL Analytics Chatbot",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STARTUP / SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    
    # Проверить подключение к БД
    try:
        count = db.get_row_count()
        logger.info(f"✅ Database ready: {count:,} rows in {settings.table_name}")
    except Exception as e:
        logger.warning(f"⚠️ Database not loaded: {e}")
        logger.info(f"💡 Run: python -c 'from database import db; db.load_parquet()'")
    
    # Проверить подключение к NLP
    if nlp_client.health_check():
        logger.info(f"✅ NLP model connected: {settings.nlp_model_url}")
    else:
        logger.warning(f"⚠️ NLP model not available")
    
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info("🛑 Shutting down...")
    db.close()

# ============================================
# ENDPOINTS
# ============================================

@app.get("/", tags=["Root"])
def root():
    """Корневой endpoint"""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Проверка работоспособности"""
    
    # Проверка БД
    try:
        db.get_row_count()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Проверка NLP
    nlp_status = "connected" if nlp_client.health_check() else "disconnected"
    
    return HealthResponse(
        status="ok" if db_status == "connected" and nlp_status == "connected" else "degraded",
        database=db_status,
        nlp_model=nlp_status,
        timestamp=datetime.now().isoformat(),
        version=settings.app_version
    )

@app.post("/ask", response_model=QueryResponse, tags=["Analytics"])
async def ask_question(request: QueryRequest):
    """
    Главный endpoint: Natural Language → SQL → Results
    """
    start_time = time.time()
    user_query = request.query
    
    logger.info(f"📝 New query: '{user_query}'")
    
    try:
        # ШАГ 1: Генерация SQL через NLP модель
        try:
            nlp_start = time.time()
            sql = nlp_client.generate_sql(user_query)
            nlp_time = time.time() - nlp_start
            
            logger.info(f"🤖 NLP generated SQL in {nlp_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ NLP generation failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"NLP model error: {str(e)}"
            )
        
        # ШАГ 2: Санитизация SQL
        sql = sanitize_sql(sql)
        logger.debug(f"🧹 Sanitized SQL: {sql}")
        
        # ШАГ 3: Валидация безопасности
        is_valid, error_msg = validate_sql_security(sql)
        if not is_valid:
            logger.warning(f"⚠️ SQL validation failed: {error_msg}")
            db.log_query(user_query, sql, False, error_msg, 0, 0)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ШАГ 4: Валидация структуры
        is_valid, error_msg = validate_sql_structure(sql)
        if not is_valid:
            logger.warning(f"⚠️ SQL structure invalid: {error_msg}")
            db.log_query(user_query, sql, False, error_msg, 0, 0)
            raise HTTPException(status_code=400, detail=error_msg)
        
        # ШАГ 5: Выполнение SQL на БД
        try:
            db_start = time.time()
            results = db.execute_sql(sql)
            db_time = time.time() - db_start
            
            # Получить названия столбцов
            columns = list(results[0].keys()) if results else []
            count = len(results)
            
            logger.info(f"💾 Query executed in {db_time:.2f}s, returned {count} rows")
            
        except Exception as e:
            logger.error(f"❌ Database execution failed: {e}")
            db.log_query(user_query, sql, False, str(e), 0, 0)
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )
        
        # ШАГ 6: Логирование и возврат результата
        total_time = time.time() - start_time
        db.log_query(user_query, sql, True, None, total_time, count)
        
        logger.info(f"✅ Query completed in {total_time:.2f}s")
        
        return QueryResponse(
            success=True,
            sql=sql,
            results=results,
            columns=columns,
            count=count,
            execution_time=round(total_time, 3),
            error=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/examples", response_model=ExamplesResponse, tags=["Examples"])
def get_examples():
    """Получить примеры запросов"""
    return ExamplesResponse(
        examples=[
            "Top 5 merchants by revenue in Kazakhstan",
            "Total transactions in Almaty in 2024",
            "Average transaction amount by wallet type",
            "Decline rate in October",
            "Transactions above 10000 KZT",
            "Monthly transaction trends",
            "Merchants with most transactions",
            "Count transactions by payment method"
        ]
    )

@app.get("/schema", response_model=SchemaResponse, tags=["Schema"])
def get_schema():
    """Получить схему таблицы"""
    try:
        schema = db.get_schema()
        total_rows = db.get_row_count()
        
        return SchemaResponse(
            table=settings.table_name,
            columns=schema,
            total_rows=total_rows
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/logs", tags=["Logs"])
def get_logs(limit: int = 50):
    """Получить последние логи запросов (для audit)"""
    try:
        logs = db.get_logs(limit=limit)
        return {
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-history", tags=["Utility"])
def clear_conversation_history():
    """Очистить историю разговора с NLP моделью"""
    try:
        nlp_client.clear_history()
        return {"message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ЗАПУСК (для разработки)
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )