"""
Тест интеграции с NLP моделью через Gradio Client
"""
import sys
from nlp_client import nlp_client

def main():
    print("="*70)
    print("🧪 ТЕСТ ИНТЕГРАЦИИ С NLP МОДЕЛЬЮ")
    print("="*70)
    print()
    
    # Тестовые запросы
    test_queries = [
        "show me top 5 transactions",
        "Top 5 merchants in Kazakhstan",
        "Сколько транзакций в Алматы",
        "transactions in October 2024",
    ]
    
    print(f"📝 Будем тестировать {len(test_queries)} запросов:\n")
    for i, q in enumerate(test_queries, 1):
        print(f"   {i}. {q}")
    
    print("\n" + "="*70)
    print("🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ")
    print("="*70 + "\n")
    
    # Health check сначала
    print("🏥 Health Check...")
    if nlp_client.health_check():
        print("   ✅ NLP model is available\n")
    else:
        print("   ❌ NLP model is NOT available")
        print("   ⚠️ Stopping tests\n")
        return
    
    # Тестируем каждый запрос
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print("-"*70)
        print(f"\n📌 TEST {i}/{len(test_queries)}")
        print(f"Query: {query}\n")
        
        try:
            sql = nlp_client.generate_sql(query)
            
            print(f"\n✅ SUCCESS!")
            print(f"Generated SQL:")
            print(f"┌{'─'*66}┐")
            
            # Форматировать SQL для красивого вывода
            sql_lines = sql.split('\n') if '\n' in sql else [sql[i:i+64] for i in range(0, len(sql), 64)]
            for line in sql_lines:
                print(f"│ {line:<64} │")
            
            print(f"└{'─'*66}┘\n")
            
            results.append({
                "query": query,
                "success": True,
                "sql": sql
            })
            
        except Exception as e:
            print(f"\n❌ FAILED!")
            print(f"Error: {e}\n")
            
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Итоговая статистика
    print("\n" + "="*70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*70)
    
    success_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    
    print(f"\n✅ Успешных: {success_count}/{total_count}")
    print(f"❌ Провалено: {total_count - success_count}/{total_count}")
    
    if success_count > 0:
        print(f"\n🎉 ИНТЕГРАЦИЯ РАБОТАЕТ! ({success_count}/{total_count} запросов)")
    else:
        print(f"\n⚠️ ИНТЕГРАЦИЯ НЕ РАБОТАЕТ!")
    
    print("\n" + "="*70)
    
    # Детальные результаты
    print("\n📋 ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ:\n")
    
    for i, result in enumerate(results, 1):
        if result["success"]:
            print(f"{i}. ✅ {result['query']}")
            print(f"   SQL: {result['sql'][:80]}...")
        else:
            print(f"{i}. ❌ {result['query']}")
            print(f"   Error: {result['error']}")
        print()
    
    print("="*70)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Тестирование прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Критическая ошибка: {e}")
        sys.exit(1)