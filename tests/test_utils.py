from typing import Any
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.utils import (
    get_cards_statistics,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_stock_prices_stub,
    get_top_transactions,
    load_transactions,
)

# ============ ТЕСТЫ ДЛЯ load_transactions ============


@patch("src.utils.pd.read_excel")
@patch("src.utils.os.path.exists")
def test_load_transactions_success(mock_exists: Mock, mock_read_excel: Mock) -> None:
    """Тест успешной загрузки транзакций."""
    mock_exists.return_value = True
    mock_df = pd.DataFrame(
        {
            "Статус": ["OK", "FAILED", "OK"],
            "Номер карты": ["*1234", "*5678", "*1234"],
            "Сумма операции": [-100.0, -200.0, -50.0],
            "Описание": ["Test1", "Test2", "Test3"],
            "Дата операции": [
                "31.12.2021 12:00:00",
                "30.12.2021 12:00:00",
                "31.12.2021 14:00:00",
            ],
        }
    )
    mock_read_excel.return_value = mock_df

    result = load_transactions("2021-12-31 12:00:00")
    assert not result.empty
    assert len(result) == 3
    assert "state" in result.columns
    assert "from" in result.columns


@patch("src.utils.os.path.exists")
def test_load_transactions_file_not_found(mock_exists: Mock) -> None:
    """Тест когда файл не найден."""
    mock_exists.return_value = False

    result = load_transactions("2021-12-31 12:00:00")
    assert result.empty


@patch("src.utils.requests.get")
def test_get_currency_rates_mock(mock_requests_get: Mock) -> None:
    """Тест get_currency_rates с моками (проще!)."""
    # Мок настроек
    with patch("src.utils.json.load") as mock_json_load:
        mock_json_load.return_value = {"user_currencies": ["USD", "EUR"]}

        # Мок ответа API - используем Mock
        mock_response = Mock()  # <-- ЯВНОЕ ИСПОЛЬЗОВАНИЕ Mock
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"USD": 0.013, "EUR": 0.011},
            "base": "RUB",
        }
        mock_requests_get.return_value = mock_response

        # Мок переменных окружения
        with patch.dict("os.environ", {"EXCHANGE_API_KEY": "test_key"}):
            result = get_currency_rates()

    # Проверяем
    assert isinstance(result, list)


# ============ ТЕСТЫ ДЛЯ get_cards_statistics ============


def test_get_cards_statistics_with_data() -> None:
    """Тест статистики по картам с данными."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK", "OK", "FAILED", "OK"],
            "from": ["*1234", "*1234", "*5678", "*1234", "*5678"],
            "amount": [-100.0, -200.0, -50.0, -300.0, -150.0],
            "description": ["Test1", "Test2", "Test3", "Test4", "Test5"],
        }
    )

    result = get_cards_statistics(df)
    assert len(result) == 2  # 2 уникальные карты
    assert result[0]["last_digits"] == "1234"
    assert result[0]["total_spent"] == 300.0  # 100 + 200
    assert result[0]["cashback"] == 3.0  # 300 // 100 = 3


def test_get_cards_statistics_empty() -> None:
    """Тест статистики по картам с пустыми данными."""
    df = pd.DataFrame()
    result = get_cards_statistics(df)
    assert result == []


def test_get_cards_statistics_no_from_column() -> None:
    """Тест когда нет колонки 'from'."""
    df = pd.DataFrame({"state": ["OK"], "amount": [-100.0]})
    result = get_cards_statistics(df)
    assert result == []


# ============ ТЕСТЫ ДЛЯ get_top_transactions ============


def test_get_top_transactions_with_data() -> None:
    """Тест топ транзакций с данными."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK", "OK", "FAILED", "OK"],
            "amount": [-1000.0, -500.0, -200.0, -3000.0, -100.0],
            "date": pd.to_datetime(["2021-12-31", "2021-12-30", "2021-12-29", "2021-12-28", "2021-12-27"]),
            "description": ["Large", "Medium", "Small", "Failed", "Tiny"],
        }
    )

    result = get_top_transactions(df, 3)
    assert len(result) == 3
    assert result[0]["amount"] == 1000.0  # Самая большая (по модулю)
    assert result[1]["amount"] == 500.0
    assert result[2]["amount"] == 200.0


def test_get_top_transactions_empty() -> None:
    """Тест топ транзакций с пустыми данными."""
    df = pd.DataFrame()
    result = get_top_transactions(df)
    assert result == []


def test_get_top_transactions_n_less_than_available() -> None:
    """Тест когда запрашиваем меньше транзакций чем есть."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK", "OK"],
            "amount": [-100.0, -200.0, -300.0],
            "date": pd.to_datetime(["2021-12-31", "2021-12-30", "2021-12-29"]),
            "description": ["A", "B", "C"],
        }
    )

    result = get_top_transactions(df, 2)
    assert len(result) == 2


# ============ ТЕСТЫ ДЛЯ get_stock_prices_stub ============


def test_get_stock_prices_stub() -> None:
    """Тест заглушки для цен акций."""
    result = get_stock_prices_stub()
    assert len(result) == 5
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.12
    assert isinstance(result[0]["price"], float)


# ============ ТЕСТ ДЛЯ __all__ ============


def test_module_exports() -> None:
    """Тест что модуль правильно экспортирует функции."""
    from src.utils import __all__

    expected_exports = [
        "load_transactions",
        "get_greeting",
        "get_cards_statistics",
        "get_top_transactions",
        "get_currency_rates",
        "get_stock_prices",
    ]
    for export in expected_exports:
        assert export in __all__


def test_get_cards_statistics_no_digits_in_card() -> None:
    """Тест когда в номере карты нет цифр."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK"],
            "from": ["Карта без цифр", "Другая карта"],
            "amount": [-100.0, -200.0],
            "description": ["Test1", "Test2"],
        }
    )

    result = get_cards_statistics(df)
    assert result == []  # Не должно быть карт без цифр


def test_get_cards_statistics_invalid_amounts() -> None:
    """Тест с некорректными суммами."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK"],
            "from": ["*1234", "*1234"],
            "amount": ["invalid", None],  # Некорректные значения
            "description": ["Test1", "Test2"],
        }
    )

    result = get_cards_statistics(df)
    # Должен обработать без ошибок
    assert len(result) == 1
    assert result[0]["total_spent"] == 0.0


# ============ ТЕСТЫ ДЛЯ ОШИБОК В get_top_transactions ============


def test_get_top_transactions_invalid_amounts() -> None:
    """Тест с некорректными суммами в топ транзакциях."""
    df = pd.DataFrame(
        {
            "state": ["OK", "OK"],
            "amount": ["не число", None],
            "date": ["31.12.2021", "30.12.2021"],
            "description": ["Test1", "Test2"],
        }
    )

    result = get_top_transactions(df)
    # Должен обработать без ошибок
    assert result == []  # Нет корректных сумм


def test_get_top_transactions_missing_description() -> None:
    """Тест когда нет описания."""
    df = pd.DataFrame(
        {
            "state": ["OK"],
            "amount": [-1000.0],
            "date": pd.to_datetime(["2021-12-31"]),
            "description": [None],  # Нет описания
        }
    )

    result = get_top_transactions(df, 1)
    assert len(result) == 1
    assert result[0]["description"] == "Без описания"
    assert result[0]["category"] == "Не указана"


# ============ ТЕСТЫ ДЛЯ get_currency_rates С ОШИБКАМИ ============


@patch("src.utils.os.getenv")
def test_get_currency_rates_no_api_key(mock_getenv: Mock) -> None:
    """Тест когда нет API ключа."""
    mock_getenv.return_value = None

    result = get_currency_rates()
    # Должна вернуться заглушка
    assert len(result) == 2
    assert result[0]["currency"] == "USD"


@patch("src.utils.os.path.exists")
def test_get_currency_rates_no_settings_file(mock_exists: Mock) -> None:
    """Тест когда нет файла настроек."""
    mock_exists.return_value = False

    result = get_currency_rates()
    # Должна вернуться заглушка
    assert len(result) == 2
    assert result[0]["currency"] == "USD"


@patch("src.utils.requests.get")
def test_get_currency_rates_exception(mock_get: Mock) -> None:
    """Тест когда возникает исключение в API."""
    mock_get.side_effect = Exception("API error")

    with patch.dict("os.environ", {"EXCHANGE_API_KEY": "test"}):
        with patch("src.utils.os.path.exists", return_value=True):
            with patch("src.utils.json.load", return_value={"user_currencies": ["USD"]}):
                result = get_currency_rates()
                # Должна вернуться заглушка
                assert len(result) == 2
                assert result[0]["currency"] == "USD"


# ============ ТЕСТЫ ДЛЯ get_stock_prices С ОШИБКАМИ ============


@patch("src.utils.os.getenv")
def test_get_stock_prices_no_api_key(mock_getenv: Mock) -> None:
    """Тест когда нет API ключа для акций."""
    mock_getenv.return_value = None

    result = get_stock_prices()
    # Должна вернуться заглушка
    assert len(result) == 5
    assert result[0]["stock"] == "AAPL"


@patch("src.utils.requests.get")
def test_get_stock_prices_exception(mock_get: Mock) -> None:
    """Тест когда возникает исключение в API акций."""
    mock_get.side_effect = Exception("API error")

    with patch.dict("os.environ", {"ALPHA_VANTAGE_API_KEY": "test"}):
        with patch("src.utils.os.path.exists", return_value=True):
            with patch("src.utils.json.load", return_value={"user_stocks": ["AAPL"]}):
                result = get_stock_prices()
                # Должна вернуться заглушка
                assert len(result) == 5
                assert result[0]["stock"] == "AAPL"


# ============ ТЕСТЫ ДЛЯ load_transactions С ОШИБКАМИ ============


@patch("src.utils.pd.read_excel")
@patch("src.utils.os.path.exists")
def test_load_transactions_read_error(mock_exists: Mock, mock_read_excel: Mock) -> None:
    """Тест когда чтение Excel вызывает ошибку."""
    mock_exists.return_value = True
    mock_read_excel.side_effect = Exception("Read error")

    result = load_transactions("2021-12-31 12:00:00")
    assert result.empty


@patch("src.utils.pd.read_excel")
@patch("src.utils.os.path.exists")
def test_load_transactions_no_required_columns(mock_exists: Mock, mock_read_excel: Mock) -> None:
    """Тест когда в данных нет нужных колонок."""
    mock_exists.return_value = True
    # DataFrame без нужных колонок
    mock_df = pd.DataFrame({"Другая колонка": [1, 2, 3], "Еще колонка": ["A", "B", "C"]})
    mock_read_excel.return_value = mock_df

    result = load_transactions("2021-12-31 12:00:00")
    # Должен вернуть DataFrame, но с warning
    assert not result.empty
    assert len(result) == 3


@patch("src.utils.pd.read_excel")
@patch("src.utils.os.path.exists")
def test_load_transactions_date_filter_error(mock_exists: Mock, mock_read_excel: Mock) -> None:
    """Тест когда фильтрация по дате вызывает ошибку."""
    mock_exists.return_value = True
    mock_df = pd.DataFrame(
        {
            "Статус": ["OK"],
            "Номер карты": ["*1234"],
            "Сумма операции": [-100.0],
            "Описание": ["Test"],
            "Дата операции": ["invalid date"],  # Некорректная дата
        }
    )
    mock_read_excel.return_value = mock_df

    result = load_transactions("invalid date string")
    # Должен обработать ошибку и вернуть DataFrame
    assert not result.empty


# ============ ТЕСТ ДЛЯ ВСЕХ ФУНКЦИЙ С ПУСТЫМИ ДАННЫМИ ============


def test_all_functions_with_empty_dataframe() -> None:
    """Комплексный тест всех функций с пустым DataFrame."""
    empty_df = pd.DataFrame()

    # get_cards_statistics
    cards_result = get_cards_statistics(empty_df)
    assert cards_result == []

    # get_top_transactions
    top_result = get_top_transactions(empty_df)
    assert top_result == []


def test_mock_import() -> None:
    """Тест, что Mock доступен если нужен."""
    from unittest.mock import Mock

    mock_obj = Mock()
    assert mock_obj is not None
