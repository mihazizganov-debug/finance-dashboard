from typing import Any
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import json

from src.views import main_page

# ============ ФИКСТУРА ============


@pytest.fixture
def fake_transactions() -> pd.DataFrame:
    """Тестовые данные транзакций."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2023-09-01", "2023-09-05"]),
            "state": ["EXECUTED", "EXECUTED"],
            "from": ["Visa 1234567890123456", "Mastercard 9876543210987654"],
            "amount": ["1000 USD", "2500 EUR"],
            "description": ["Покупка", "Оплата"],
        }
    )


# ============ ТЕСТ ДЛЯ ПРОВЕРКИ MOCK ============


def test_mock_object() -> None:
    """Тест, что Mock импортирован и может использоваться."""
    mock_obj = Mock()
    mock_obj.some_method.return_value = 42
    assert mock_obj.some_method() == 42


# ============ ПАРАМЕТРИЗОВАННЫЕ ТЕСТЫ ============


@pytest.mark.parametrize(
    "time,greeting",
    [
        ("2023-09-05 08:00:00", "Доброе утро"),
        ("2023-09-05 14:00:00", "Добрый день"),
        ("2023-09-05 20:00:00", "Добрый вечер"),
        ("2023-09-05 02:00:00", "Доброй ночи"),
    ],
)
def test_greetings_parametrized(time: str, greeting: str, fake_transactions: pd.DataFrame) -> None:
    """Параметризованный тест приветствий."""
    with patch("src.views.load_transactions") as mock_load, patch("src.views.get_greeting") as mock_greet, patch(
        "src.views.get_cards_statistics"
    ) as mock_cards, patch("src.views.get_top_transactions") as mock_top, patch(
        "src.views.get_currency_rates"
    ) as mock_currency, patch(
        "src.views.get_stock_prices"
    ) as mock_stocks:
        # Настраиваем моки
        mock_load.return_value = fake_transactions
        mock_greet.return_value = greeting
        mock_cards.return_value = []
        mock_top.return_value = []
        mock_currency.return_value = []
        mock_stocks.return_value = []

        # Вызываем
        result_str = main_page(time)
        result = json.loads(result_str)

        # Проверяем
        assert result["greeting"] == greeting
        assert result["cards"] == []
        assert result["top_transactions"] == []


# ============ ТЕСТЫ С MOCK ============


@patch("src.views.load_transactions")
@patch("src.views.get_greeting")
@patch("src.views.get_cards_statistics")
@patch("src.views.get_top_transactions")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
def test_full_mock(
    mock_stocks: Mock,
    mock_currency: Mock,
    mock_top: Mock,
    mock_cards: Mock,
    mock_greet: Mock,
    mock_load: Mock,
    fake_transactions: pd.DataFrame,
) -> None:
    """Полный тест с моками."""
    # Настраиваем моки
    mock_load.return_value = fake_transactions
    mock_greet.return_value = "Добрый день"
    mock_cards.return_value = [{"last_digits": "3456", "total_spent": 1000.0, "cashback": 10.0}]
    mock_top.return_value = [
        {
            "date": "01.09.2023",
            "amount": 1000.0,
            "category": "Покупка",
            "description": "Покупка",
        }
    ]

    # Используем Mock явно
    mock_currency_response = Mock()
    mock_currency_response.return_value = [{"currency": "USD", "rate": 75.0}]
    mock_currency.side_effect = mock_currency_response

    mock_stocks_response = Mock()
    mock_stocks_response.return_value = [{"stock": "AAPL", "price": 150.0}]
    mock_stocks.side_effect = mock_stocks_response

    # Вызываем
    result_str = main_page("2023-09-05 12:00:00")
    result = json.loads(result_str)

    # Проверяем структуру
    assert result["greeting"] == "Добрый день"
    assert len(result["cards"]) == 1
    assert len(result["top_transactions"]) == 1
    assert len(result["currency_rates"]) == 1
    assert len(result["stock_prices"]) == 1

    # Проверяем что функции вызвались
    mock_load.assert_called_once_with("2023-09-05 12:00:00")
    mock_greet.assert_called_once_with("2023-09-05 12:00:00")
    mock_cards.assert_called_once_with(fake_transactions)
    mock_top.assert_called_once_with(fake_transactions, 5)
    mock_currency.assert_called_once()
    mock_stocks.assert_called_once()


# ============ ТЕСТ ОШИБОК ============


@patch("src.views.load_transactions")
def test_empty_data(mock_load: Mock) -> None:
    """Тест с пустыми данными."""
    # Используем Mock
    mock_df = Mock()
    mock_df.empty = True
    mock_load.return_value = mock_df

    result_str = main_page("2023-09-05 12:00:00")
    result = json.loads(result_str)

    # Должен вернуть валидный JSON
    assert isinstance(result, dict)
    assert result["cards"] == []
    assert result["top_transactions"] == []


# ============ РЕАЛЬНЫЙ ТЕСТ ============


def test_real_integration() -> None:
    """Реальный интеграционный тест."""
    # Вызываем с реальной датой
    result_str = main_page("2023-09-05 12:00:00")
    result = json.loads(result_str)

    # Проверяем базовые требования
    assert isinstance(result, dict)
    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert "date" in result

    # Проверяем типы
    assert isinstance(result["greeting"], str)
    assert isinstance(result["cards"], list)
    assert isinstance(result["top_transactions"], list)
    assert isinstance(result["currency_rates"], list)
    assert isinstance(result["stock_prices"], list)
    assert isinstance(result["date"], str)

    # Логика топ-транзакций
    assert len(result["top_transactions"]) <= 5