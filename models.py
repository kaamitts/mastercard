"""
Pydantic модели для валидации данных
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

# ============================================
# REQUEST MODELS
# ============================================

class QueryRequest(BaseModel):
    """Запрос от Frontend"""
    query: str = Field(..., min_length=1, description="User question in natural language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "Top 5 merchants by revenue in Kazakhstan"
            }
        }

# ============================================
# RESPONSE MODELS
# ============================================

class QueryResponse(BaseModel):
    """Ответ пользователю"""
    success: bool = Field(..., description="Whether query was successful")
    sql: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="Query results")
    columns: List[str] = Field(default_factory=list, description="Column names")
    count: int = Field(..., description="Number of rows returned")
    execution_time: float = Field(..., description="Total execution time in seconds")
    error: Optional[str] = Field(None, description="Error message if failed")

class HealthResponse(BaseModel):
    """Статус работоспособности"""
    status: str
    database: str
    nlp_model: str
    timestamp: str
    version: str

class ExamplesResponse(BaseModel):
    """Примеры запросов"""
    examples: List[str]

class SchemaResponse(BaseModel):
    """Схема таблицы"""
    table: str
    columns: Dict[str, str]
    total_rows: int

class LogEntry(BaseModel):
    """Запись лога"""
    timestamp: str
    user_query: str
    generated_sql: str
    success: bool
    error_message: Optional[str]
    execution_time: float
    rows_returned: int