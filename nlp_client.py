"""
Клиент для взаимодействия с NLP моделью на HuggingFace
"""
from gradio_client import Client
from typing import Optional
from logger import logger
from config import settings

class NLPClient:
    """Клиент для NLP модели на HuggingFace Gradio"""
    
    def __init__(self):
        self.space_url = settings.nlp_model_url
        self.client = None
        self.conversation_history = []
        self._connect()
    
    def _connect(self):
        """Подключиться к Gradio Space"""
        try:
            logger.info(f"🔗 Connecting to NLP model: {self.space_url}")
            self.client = Client(self.space_url)
            logger.info("✅ Connected to NLP model")
        except Exception as e:
            logger.error(f"❌ Failed to connect to NLP model: {e}")
            self.client = None
    
    def generate_sql(self, query: str) -> str:
        """
        Сгенерировать SQL из естественного языка
        
        Args:
            query: Вопрос на естественном языке
            
        Returns:
            str: SQL запрос
        """
        if not self.client:
            self._connect()
        
        if not self.client:
            raise Exception("NLP model is not available")
        
        logger.info(f"🤖 Generating SQL for query: '{query}'")
        
        try:
            # Вызов Gradio функции
            result = self.client.predict(
                query,
                self.conversation_history,
                api_name="/handle_submit"
            )
            
            # result = (your_question, conversation)
            if isinstance(result, tuple) and len(result) >= 2:
                updated_conversation = result[1]
                
                if updated_conversation and len(updated_conversation) > 0:
                    last_pair = updated_conversation[-1]
                    
                    if isinstance(last_pair, (list, tuple)) and len(last_pair) >= 2:
                        sql_response = last_pair[1]
                        
                        # Обновить историю
                        self.conversation_history = updated_conversation
                        
                        # Извлечь SQL
                        sql = self._extract_sql(sql_response)
                        
                        if sql:
                            logger.info(f"✅ Generated SQL: {sql[:100]}...")
                            return sql
                        else:
                            raise Exception(f"Could not extract SQL from response")
                    else:
                        raise Exception(f"Unexpected conversation format")
                else:
                    raise Exception("Empty conversation returned")
            else:
                raise Exception(f"Unexpected result format")
                
        except Exception as e:
            logger.error(f"❌ NLP model error: {e}")
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def _extract_sql(self, response: str) -> Optional[str]:
        """Извлечь SQL из ответа модели"""
        if not response:
            return None
        
        # Убрать артефакты промпта
        response = response.replace("[/SYS];", "").replace("[/SYS]", "")
        response = response.replace("[/INST]", "").replace("[INST]", "")
        response = response.strip()
        
        # Если ответ содержит markdown code block
        if "```sql" in response:
            start = response.find("```sql") + 6
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        # Если ответ содержит обычный code block
        if "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                sql = response[start:end].strip()
                if sql.startswith("sql\n"):
                    sql = sql[4:].strip()
                return sql
        
        # Если SQL без обертки
        if response.upper().startswith("SELECT"):
            return response
        
        return response
    
    def clear_history(self):
        """Очистить историю разговора"""
        self.conversation_history = []
        logger.info("🗑️ Conversation history cleared")
    
    def health_check(self) -> bool:
        """Проверить доступность NLP модели"""
        try:
            if not self.client:
                self._connect()
            return self.client is not None
        except:
            return False

# Глобальный экземпляр
nlp_client = NLPClient()