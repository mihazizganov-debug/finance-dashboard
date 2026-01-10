import json
from src.utils import (
    get_cards_statistics,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    load_transactions,
)


def main_page(date_string: str) -> str:  # ← ИЗМЕНИ: было dict, стало str
    """
    Главная функция. Принимает дату в формате 'YYYY-MM-DD HH:MM:SS'.
    Возвращает JSON-строку для веб-страницы (по ТЗ).
    """
    # Загружаем данные
    df = load_transactions(date_string)

    date_only = date_string.split()[0] if " " in date_string else date_string

    # Формируем словарь-ответ
    response_dict = {
        "greeting": get_greeting(date_string),
        "cards": get_cards_statistics(df),
        "top_transactions": get_top_transactions(df, 5),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
        "date": date_only
    }

    # Преобразуем в JSON-строку
    return json.dumps(response_dict, ensure_ascii=False, indent=2)