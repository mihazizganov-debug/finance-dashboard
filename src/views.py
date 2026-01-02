from src.utils import (
    get_cards_statistics,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    load_transactions,
)


def main_page(date_string: str) -> dict:
    """
    Главная функция. Принимает дату в формате 'YYYY-MM-DD HH:MM:SS'.
    Возвращает JSON для веб-страницы.
    """
    # Загружаем данные
    df = load_transactions(date_string)

    # Формируем ответ
    return {
        "greeting": get_greeting(date_string),
        "cards": get_cards_statistics(df),
        "top_transactions": get_top_transactions(df, 5),
        "currency_rates": get_currency_rates(),
        "stock_prices": get_stock_prices(),
    }
