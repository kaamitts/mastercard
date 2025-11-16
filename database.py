"""
Работа с базой данных DuckDB
"""
import duckdb
import os
from typing import List, Dict
from datetime import datetime
from logger import logger
from config import settings

class Database:
    """Класс для работы с DuckDB"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.database_path
        self.conn = None
        self._connect()
        self._init_logs_table()
    
    def _connect(self):
        """Подключиться к базе данных"""
        try:
            # FIX: Используем read_only если не главный процесс
            import os
            if os.getenv("UVICORN_WORKER_ID"):
                # Worker process - read-only
                self.conn = duckdb.connect(self.db_path, read_only=True)
                logger.info(f"✅ DuckDB connected (read-only): {self.db_path}")
            else:
                # Main process
                self.conn = duckdb.connect(self.db_path)
                logger.info(f"✅ DuckDB connected: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to DuckDB: {e}")
            raise
    
    def _init_logs_table(self):
        """Создать таблицу для логов"""
        try:
            # Удалить старую таблицу если есть проблемы
            self.conn.execute("DROP TABLE IF EXISTS query_logs")
            self.conn.execute("DROP SEQUENCE IF EXISTS query_logs_seq")
            
            # Создать заново с правильным AUTO_INCREMENT
            self.conn.execute("""
                CREATE SEQUENCE query_logs_seq START 1;
            """)
            
            self.conn.execute("""
                CREATE TABLE query_logs (
                    id INTEGER PRIMARY KEY DEFAULT nextval('query_logs_seq'),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    user_query TEXT,
                    generated_sql TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    execution_time FLOAT,
                    rows_returned INTEGER
                )
            """)
            
            logger.debug("✅ Logs table initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not create logs table: {e}")
        
    def load_parquet(self, parquet_file: str = None, table_name: str = None):
        """Загрузить parquet файл как таблицу"""
        parquet_file = parquet_file or settings.dataset_path
        table_name = table_name or settings.table_name
        
        if not os.path.exists(parquet_file):
            raise FileNotFoundError(f"Dataset not found: {parquet_file}")
        
        logger.info(f"📊 Loading dataset from {parquet_file}...")
        
        try:
            # DuckDB читает parquet напрямую
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS 
                SELECT * FROM read_parquet('{parquet_file}')
            """)
            
            # Статистика
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            logger.info(f"✅ Loaded {count:,} rows into '{table_name}'")
            
            # Показать схему
            self._log_schema(table_name)
            
            return count
            
        except Exception as e:
            logger.error(f"❌ Failed to load parquet: {e}")
            raise
    
    def _log_schema(self, table_name: str):
        """Вывести схему таблицы в лог"""
        try:
            columns = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            logger.info(f"📋 Table '{table_name}' schema:")
            for col in columns[:10]:
                logger.info(f"   {col[0]:30s} {col[1]}")
            if len(columns) > 10:
                logger.info(f"   ... and {len(columns) - 10} more columns")
        except Exception as e:
            logger.warning(f"⚠️ Could not log schema: {e}")
    
    def execute_sql(self, sql_query: str, timeout: int = None) -> List[Dict]:
        """Выполнить SQL запрос"""
        timeout = timeout or settings.query_timeout
        
        try:
            # Установить таймаут
            #self.conn.execute(f"SET query_timeout = '{timeout}s'")
            
            # Выполнить запрос
            result = self.conn.execute(sql_query)
            rows = result.fetchall()
            
            # Получить названия столбцов
            columns = [desc[0] for desc in result.description] if result.description else []
            
            # Конвертировать в список словарей
            results = []
            for row in rows:
                row_dict = {}
                for i, col_name in enumerate(columns):
                    value = row[i]
                    
                    # Конвертировать специальные типы
                    if hasattr(value, '__float__'):
                        value = float(value)
                    elif hasattr(value, '__int__'):
                        value = int(value)
                    
                    row_dict[col_name] = value
                
                results.append(row_dict)
            
            # Ограничить количество результатов
            if len(results) > settings.max_results:
                logger.warning(f"⚠️ Results limited to {settings.max_results} rows")
                results = results[:settings.max_results]
            
            logger.debug(f"💾 Query returned {len(results)} rows")
            return results
            
        except Exception as e:
            logger.error(f"❌ SQL execution failed: {e}")
            raise Exception(f"Database error: {str(e)}")
    
    def get_schema(self, table_name: str = None) -> Dict[str, str]:
        """Получить схему таблицы"""
        table_name = table_name or settings.table_name
        try:
            columns = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
            return {col[0]: col[1] for col in columns}
        except Exception as e:
            logger.error(f"❌ Failed to get schema: {e}")
            raise
    
    def get_row_count(self, table_name: str = None) -> int:
        """Получить количество строк"""
        table_name = table_name or settings.table_name
        try:
            count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            return count
        except Exception as e:
            logger.error(f"❌ Failed to get row count: {e}")
            return 0
    
    def log_query(self, user_query: str, sql: str, success: bool, 
               error: str = None, execution_time: float = 0, rows: int = 0):
        """Сохранить запрос в лог-таблицу"""
        try:
            self.conn.execute("""
                INSERT INTO query_logs 
                (user_query, generated_sql, success, error_message, execution_time, rows_returned)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [user_query, sql, success, error, execution_time, rows])
        except Exception as e:
            logger.warning(f"⚠️ Failed to log query: {e}")
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Получить последние логи"""
        try:
            logs = self.execute_sql(f"""
                SELECT * FROM query_logs 
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """)
            return logs
        except Exception as e:
            logger.warning(f"⚠️ Failed to get logs: {e}")
            return []
    
    def close(self):
        """Закрыть соединение"""
        if self.conn:
            self.conn.close()
            logger.info("🔒 Database connection closed")

# Глобальный экземпляр
db = Database()