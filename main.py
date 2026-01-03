import json
import logging

from src.services import investment_bank
from src.views import main_page

# Отключаем логи
logging.getLogger().setLevel(logging.CRITICAL)

if __name__ == "__main__":
    print("=" * 60)
    print("КУРСОВАЯ РАБОТА: ФИНАНСОВЫЙ ДАШБОРД")
    print("=" * 60)

    # 1. Существующая функция main_page()
    print("\n1. Функция main_page() - возвращает JSON для веб-страницы")
    print("Вход: '2021-12-31 16:44:00'")

    result1 = main_page("2021-12-31 16:44:00")
    print("Вывод JSON:")
    print(json.dumps(result1, ensure_ascii=False, indent=2))

    # 2. Новая функция investment_bank() - курсовая
    print("\n2. Функция investment_bank() - сервис 'Инвесткопилка' (курсовая)")

    transactions = [
        {"Дата операции": "2024-01-15", "Сумма операции": 1712},
        {"Дата операции": "2024-01-20", "Сумма операции": 548.50},
        {"Дата операции": "2024-02-01", "Сумма операции": 1000},
    ]

    print("Входные данные:")
    print("  • Месяц: 2024-01")
    print("  • Лимит: 50 ₽")
    print(f"  • Транзакций: {len(transactions)}")

    try:
        result2 = investment_bank("2024-01", transactions, 50)

        print("\nВывод (JSON-ответ):")  # ← Убрал f
        print(result2)  # Это будет JSON-строка

        # Парсим JSON чтобы показать структуру
        data = json.loads(result2)
        print("\nСтруктура JSON:")  # ← Убрал f
        print(f"  • Месяц: {data['month']}")
        print(f"  • Сумма: {data['investment_total']} ₽")
        print(f"  • Лимит: {data['rounding_limit']} ₽")

    except ValueError as e:
        print(f"\n❌ Ошибка валидации: {e}")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
