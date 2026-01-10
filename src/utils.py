"""
Модуль utils.py для курсовой работы.
Вспомогательные функции для страницы "Главная".
"""

import datetime
import json
import logging
import os
import re
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def safe_extract_amount(value: Any) -> float:
    """
    Безопасно извлекает сумму из значения.
    Возвращает абсолютное значение суммы.
    """
    if pd.isna(value):
        return 0.0
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return 0.0


def extract_last_digits(card_str: Any) -> str:
    """
    Извлекает последние 4 цифры из номера карты.
    Возвращает пустую строку если цифр нет.
    """
    if pd.isna(card_str):
        return ""

    # Ищем 4+ цифр в строке
    matches = re.findall(r"\d{4,}", str(card_str))
    if not matches:
        return ""

    return matches[0][-4:]  # Последние 4 цифры


def format_date_for_transaction(date_value: Any) -> str:
    """
    Форматирует дату для транзакции в формат 'dd.mm.yyyy'.
    Возвращает значение по умолчанию при ошибке.
    """
    if pd.isna(date_value):
        return "01.01.2024"  # Значение по умолчанию

    try:
        if isinstance(date_value, (datetime.datetime, pd.Timestamp)):
            return date_value.strftime("%d.%m.%Y")
        elif isinstance(date_value, str):
            # Убираем время если есть
            date_part = date_value.split()[0] if " " in date_value else date_value

            # Пробуем распарсить
            for fmt in ["%d.%m.%Y", "%Y-%m-%d"]:
                try:
                    dt = datetime.datetime.strptime(date_part, fmt)
                    return dt.strftime("%d.%m.%Y")
                except ValueError:
                    continue
    except Exception:
        pass

    return "01.01.2024"


def extract_category_from_description(description: Any) -> tuple[str, str]:
    """
    Извлекает категорию и описание из строки описания.
    Возвращает кортеж (категория, описание).
    """
    if pd.isna(description):
        return "Не указана", "Без описания"

    description_str = str(description)
    # Берем первое слово как категорию
    words = description_str.split()
    category = words[0] if words else "Не указана"

    return category, description_str


# ============ ОСНОВНЫЕ ФУНКЦИИ ============

def load_transactions(date_string: str) -> pd.DataFrame:
    """
    Загружает транзакции из Excel файла и фильтрует по текущему месяцу.

    Parameters:
    -----------
    date_string : str
        Дата в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
    --------
    pd.DataFrame
        DataFrame с транзакций за текущий месяц или пустой DataFrame в случае ошибки
    """
    try:
        # Исправляем: используем правильные переменные
        file_path_operations_xlsx = "data/operations.xlsx"
        file_path_transactions_xlsx = "data/transactions_excel.xlsx"
        file_path_transactions_xls = "data/transactions_excel.xls"

        # Пробуем в порядке приоритета
        if os.path.exists(file_path_operations_xlsx):
            df = pd.read_excel(file_path_operations_xlsx)
            logger.info(f"Загружен файл {file_path_operations_xlsx}")
        elif os.path.exists(file_path_transactions_xlsx):
            df = pd.read_excel(file_path_transactions_xlsx)
            logger.info(f"Загружен файл {file_path_transactions_xlsx}")
        elif os.path.exists(file_path_transactions_xls):
            df = pd.read_excel(file_path_transactions_xls)
            logger.info(f"Загружен файл {file_path_transactions_xls}")
        else:
            logger.error("Файл с транзакциями не найден.")
            logger.error("Проверяемые пути:")
            logger.error(f"  - {file_path_operations_xlsx}")
            logger.error(f"  - {file_path_transactions_xlsx}")
            logger.error(f"  - {file_path_transactions_xls}")
            return pd.DataFrame()

        # Переименовываем колонки согласно ТЗ
        if not df.empty:
            # Создаем словарь для переименования, но только для существующих колонок
            column_mapping = {}
            possible_columns = {
                "Статус": "state",
                "Номер карты": "from",
                "Сумма операции": "amount",
                "Описание": "description",
                "Дата операции": "date",
            }

            for rus_name, eng_name in possible_columns.items():
                if rus_name in df.columns:
                    column_mapping[rus_name] = eng_name

            if column_mapping:
                df = df.rename(columns=column_mapping)
                logger.info(f"Переименованы колонки: {column_mapping}")

        # Фильтруем по текущему месяцу
        if not df.empty and "date" in df.columns:
            # Конвертируем дату если нужно
            df["date"] = pd.to_datetime(df["date"], format="%d.%m.%Y %H:%M:%S", errors="coerce", dayfirst=True)

            # Получаем начало месяца из входной даты
            try:
                input_date = pd.to_datetime(date_string.split()[0])
                month_start = pd.Timestamp(year=input_date.year, month=input_date.month, day=1)

                # Фильтруем данные с начала месяца
                df = df[df["date"] >= month_start]
                logger.info(f"Отфильтровано по месяцу: {month_start.date()}")
            except Exception as e:
                logger.warning(f"Ошибка фильтрации по месяцу: {e}")

        # Проверяем необходимые колонки
        required_columns = ["state", "from", "amount", "description"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            logger.warning(f"Отсутствуют необходимые колонки: {missing_columns}")

        return df

    except Exception as e:
        logger.error(f"Ошибка загрузки транзакций: {e}")
        return pd.DataFrame()


def get_greeting(date_string: str) -> str:
    """Возвращает приветствие по времени суток по российским стандартам."""
    try:
        dt = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour

        if 0 <= hour < 4:
            return "Доброй ночи"
        elif 4 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 16:
            return "Добрый день"
        else:  # 16:00 - 23:59
            return "Добрый вечер"

    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка в get_greeting: {e}")
        return "Добрый день"


def get_cards_statistics(df: pd.DataFrame) -> list:
    """Анализ по картам: последние 4 цифры, сумма расходов, кешбэк."""
    if df.empty or "from" not in df.columns:
        return []

    df = df[df["state"] == "OK"].copy()

    cards_data = []

    for card_str in df["from"].dropna().unique():
        # Извлекаем последние 4 цифры
        last_digits = extract_last_digits(card_str)
        if not last_digits:
            continue  # Пропускаем карты без цифр

        card_df = df[df["from"] == card_str]

        # Извлекаем суммы (суммы отрицательные, берем модуль)
        total = 0
        for amount in card_df["amount"]:
            if pd.notna(amount):
                # Используем безопасное извлечение суммы
                total += safe_extract_amount(amount)

        # Кешбэк: 1 рубль за каждые 100 рублей
        cashback = round(total / 100, 2)

        cards_data.append(
            {
                "last_digits": last_digits,
                "total_spent": round(total, 2),
                "cashback": round(cashback, 2),
            }
        )

    return cards_data


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> list:
    """Топ-N транзакций по сумме платежа."""
    if df.empty:
        return []

    df = df[df["state"] == "OK"].copy()

    # Извлекаем числовые суммы (берем абсолютное значение)
    amounts = []
    for idx, row in df.iterrows():
        amount_val = row["amount"]
        if pd.notna(amount_val):
            amount = safe_extract_amount(amount_val)
            if amount > 0:
                amounts.append((idx, amount))

    # Сортируем по сумме (уже абсолютной)
    amounts.sort(key=lambda x: x[1], reverse=True)

    top_transactions = []
    seen_descriptions = set()

    for i in range(min(n, len(amounts))):
        idx, amount = amounts[i]
        row = df.loc[idx]

        # Обработка даты
        date_value = row["date"]
        formatted_date = format_date_for_transaction(date_value)

        # Обработка описания
        category, description_str = extract_category_from_description(row.get("description"))

        # Проверяем на дубликаты
        key = f"{description_str}_{amount}"
        if key in seen_descriptions:
            continue
        seen_descriptions.add(key)

        top_transactions.append(
            {
                "date": formatted_date,
                "amount": round(amount, 2),
                "category": category,
                "description": description_str,
            }
        )

        if len(top_transactions) >= n:
            break

    return top_transactions


def get_currency_rates() -> list:
    """Курсы валют из API apilayer.com."""
    try:
        api_key = os.getenv("EXCHANGE_API_KEY")
        if not api_key:
            return [
                {"currency": "USD", "rate": 73.21},
                {"currency": "EUR", "rate": 87.08},
            ]

        settings_path = "user_settings.json"
        if not os.path.exists(settings_path):
            logger.warning(f"Файл настроек не найден: {settings_path}")
            return [
                {"currency": "USD", "rate": 73.21},
                {"currency": "EUR", "rate": 87.08},
            ]

        with open(settings_path, "r", encoding="utf-8-sig") as f:
            settings = json.load(f)

        currencies = settings.get("user_currencies", ["USD", "EUR"])

        # API apilayer.com (Currency Data API)
        url = "https://api.apilayer.com/exchangerates_data/latest"
        headers = {"apikey": api_key}
        params = {"base": "RUB", "symbols": ",".join(currencies)}

        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            rates = []
            for currency, rate in data.get("rates", {}).items():
                # ВАЖНО: инвертируем курс!
                # API даёт: 1 RUB = X USD
                # Нам нужно: 1 USD = 1/X RUB
                inverse_rate = 1 / rate
                rates.append({"currency": currency, "rate": round(inverse_rate, 2)})
            return rates
        else:
            logger.warning(f"Ошибка API валют: {response.status_code} - {response.text}")
            return [
                {"currency": "USD", "rate": 73.21},
                {"currency": "EUR", "rate": 87.08},
            ]

    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        return [{"currency": "USD", "rate": 73.21}, {"currency": "EUR", "rate": 87.08}]


def get_stock_prices() -> list:
    """Цены акций из API."""
    try:
        # Пробуем разные имена переменных
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY") or os.getenv("STOCK_API_KEY")
        if not api_key:
            return get_stock_prices_stub()

        # Загружаем настройки пользователя (используем utf-8-sig для BOM)
        with open("user_settings.json", "r", encoding="utf-8-sig") as f:
            settings = json.load(f)

        stocks = settings.get("user_stocks", ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

        stock_prices = []
        for stock in stocks:
            url = "https://www.alphavantage.co/query"
            params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": api_key}
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if "Global Quote" in data and "05. price" in data["Global Quote"]:
                    price = float(data["Global Quote"]["05. price"])
                    stock_prices.append({"stock": stock, "price": round(price, 2)})

        if stock_prices:
            return stock_prices
    except Exception:
        pass

    return get_stock_prices_stub()


def get_stock_prices_stub() -> list:
    """Заглушка для цен акций."""
    return [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18},
        {"stock": "GOOGL", "price": 2742.39},
        {"stock": "MSFT", "price": 296.71},
        {"stock": "TSLA", "price": 1007.08},
    ]


__all__ = [
    "load_transactions",
    "get_greeting",
    "get_cards_statistics",
    "get_top_transactions",
    "get_currency_rates",
    "get_stock_prices",
]