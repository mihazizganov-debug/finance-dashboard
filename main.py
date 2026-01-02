from src.views import main_page
import json
from datetime import datetime

if __name__ == "__main__":
    # Используем дату для демонстрации
    test_date = "2021-12-31 16:44:00"

    print(f"Используемая дата: {test_date}")

    result = main_page(test_date)

    print(f"\nПриветствие: {result['greeting']}")
    print(f"Время: 16:44")

    # Для полного вывода JSON
    if input("\nПоказать полный JSON? (y/n): ").lower() == 'y':
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
