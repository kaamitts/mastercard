from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Settings
    app_name: str = "Mastercard Analytics API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # NLP Model
    nlp_model_url: str = "https://nuraly17-futbolchik.hf.space"  
    nlp_timeout: int = 100  # 100 секунд на генерацию SQL
    
    # Database
    database_path: str = "mastercard.db"
    dataset_path: str = "data/dataset.parquet"
    table_name: str = "example_dataset"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # Query limits
    max_results: int = 10000  # Максимум строк в ответе
    query_timeout: int = 200   # Максимум секунд на SQL запрос
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/backend.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()