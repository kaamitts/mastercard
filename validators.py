import re
from typing import Tuple
from logger import logger

def validate_sql_security(sql: str) -> Tuple[bool, str]:
    """
    Проверить SQL на безопасность
    
    Returns:
        (is_valid, error_message)
    """
    if not sql or not sql.strip():
        return False, "SQL query is empty"
    
    sql_upper = sql.strip().upper()

    # Проверка 0: Если модель вернула комментарий - это ошибка
    if sql.strip().startswith("--"):
        logger.warning(f"⚠️ NLP model returned comment instead of SQL")
        return False, "NLP model did not generate valid SQL. Try rephrasing your question in English."
    
    # Проверка 1: Только SELECT запросы
    if not sql_upper.startswith("SELECT"):
        logger.warning(f"⚠️ Non-SELECT query blocked: {sql[:50]}")
        return False, "Only SELECT queries are allowed"
    
    # Проверка 2: Опасные команды
    dangerous_keywords = [
        "DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE",
        "ALTER", "CREATE", "EXEC", "EXECUTE", "GRANT", "REVOKE"
    ]
    
    for keyword in dangerous_keywords:
        if re.search(rf'\b{keyword}\b', sql_upper):
            logger.warning(f"⚠️ Dangerous keyword '{keyword}' blocked")
            return False, f"Dangerous SQL command detected: {keyword}"
    
    # Проверка 3: SQL injection паттерны
    injection_patterns = [
        (r'--', "SQL comments (--) not allowed"),
        (r'/\*', "Multi-line comments not allowed"),
        (r';\s*\w+', "Multiple statements not allowed"),
        (r'\bxp_', "System procedures not allowed"),
    ]
    
    for pattern, message in injection_patterns:
        if re.search(pattern, sql, re.IGNORECASE):
            logger.warning(f"⚠️ Injection pattern blocked: {message}")
            return False, message
    
    logger.debug(f"✅ SQL validation passed")
    return True, ""

def validate_sql_structure(sql: str) -> Tuple[bool, str]:
    """
    Проверить структуру SQL запроса
    """
    from config import settings
    
    sql_lower = sql.lower()
    table_name = settings.table_name.lower()

    # Проверка: использует таблицу transactions
    if f"from {table_name}" not in sql_lower and f"from `{table_name}`" not in sql_lower:
        logger.warning(f"⚠️ Query doesn't use '{table_name}' table")
        return False, f"Query must use '{table_name}' table"
    
    return True, ""

def sanitize_sql(sql: str) -> str:
    """
    Очистить и нормализовать SQL
    """
    # Убрать лишние пробелы
    sql = " ".join(sql.split())
    
    # Убрать точку с запятой в конце
    sql = sql.rstrip(";")
    
    return sql