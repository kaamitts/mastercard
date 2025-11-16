"""
Настройка логирования
"""
import logging
import os
from datetime import datetime
from config import settings

# Создать папку для логов
os.makedirs("logs", exist_ok=True)

# Формат логов
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

# Создать logger
logger = logging.getLogger("mastercard_backend")
logger.setLevel(getattr(logging, settings.log_level.upper()))

# Handler для файла
file_handler = logging.FileHandler(settings.log_file, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Handler для консоли
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG if settings.debug else logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# Добавить handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Функции для удобного логирования
def log_query(user_query: str, sql: str, success: bool, error: str = None):
    """Логировать запрос пользователя"""
    if success:
        logger.info(f"✅ Query: '{user_query}' | SQL: '{sql[:100]}...'")
    else:
        logger.error(f"❌ Query: '{user_query}' | Error: {error}")

def log_nlp_call(query: str, response_time: float, success: bool):
    """Логировать вызов NLP модели"""
    if success:
        logger.info(f"🤖 NLP call successful | Query: '{query}' | Time: {response_time:.2f}s")
    else:
        logger.error(f"🤖 NLP call failed | Query: '{query}'")

def log_db_query(sql: str, rows: int, execution_time: float):
    """Логировать выполнение SQL"""
    logger.info(f"💾 DB query | Rows: {rows} | Time: {execution_time:.3f}s | SQL: '{sql[:100]}...'")