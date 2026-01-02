from src.views import main_page
import json

if __name__ == "__main__":
    # Используйте дату, которая есть в данных
    # Например, если данные до 2021 года:
    result = main_page("2021-12-15 12:00:00")  # Декабрь 2021
    # Или
    # result = main_page("2021-09-05 12:00:00")  # Сентябрь 2021
    print(json.dumps(result, ensure_ascii=False, indent=2))