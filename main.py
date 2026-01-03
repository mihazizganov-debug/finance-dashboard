import json
import logging

import pandas as pd

from src.reports import spending_by_weekday
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

    # 3. Новая функция - отчет "Траты по дням недели"
    print("\n" + "=" * 60)
    print("3. Функция spending_by_weekday() - отчет 'Траты по дням недели'")

    # Создаем тестовый DataFrame
    test_data = {
        "Дата операции": [
            "2024-01-15",
            "2024-01-16",
            "2024-01-17",
            "2024-01-18",
            "2024-02-15",
            "2024-02-16",
            "2024-02-17",
            "2024-02-18",
            "2024-03-15",
            "2024-03-16",
            "2024-03-17",
            "2024-03-18",
        ],
        "Сумма операции": [1000, 1500, 2000, 2500, 1200, 1700, 2200, 2700, 1400, 1900, 2400, 2900],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Покупки"] * 3,
        "Описание": ["Обед", "Такси", "Кино", "Магазин"] * 3,
    }

    df = pd.DataFrame(test_data)

    print("\nТестовые данные (DataFrame):")
    print(f"  • Строк: {len(df)}")
    print(f"  • Колонок: {len(df.columns)}")
    print(f"  • Колонки: {list(df.columns)}")

    print("\nЗапуск отчета с датой '2024-03-20'...")
    try:
        result3 = spending_by_weekday(df, "2024-03-20")
        data3 = json.loads(result3)

        print("\nРезультат отчета:")
        print(f"  • Отчет: {data3['report']}")
        print(f"  • Период: {data3['period']['start']} - {data3['period']['end']}")
        print(f"  • Статус: {data3['status']}")

        print("\nСредние траты по дням недели:")
        for day, amount in data3["data"].items():
            print(f"  • {day}: {amount} ₽")

    except ValueError as e:
        print(f"\n❌ Ошибка валидации: {e}")
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")

    print("\n" + "=" * 60)
    print("✅ ДЕМОНСТРАЦИЯ ВСЕХ ТРЕХ ФУНКЦИЙ ЗАВЕРШЕНА")
    print("=" * 60)
