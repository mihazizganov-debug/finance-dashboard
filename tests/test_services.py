import json
import os
import sys
from typing import Any

import pytest

from src.services import investment_bank


# 1. БАЗОВЫЕ ТЕСТЫ
def test_investment_bank_basic() -> None:
    """Базовый тест работы функции"""
    result = investment_bank("2024-01", [], 50)
    data = json.loads(result)
    assert data["month"] == "2024-01"
    assert data["rounding_limit"] == 50
    assert data["investment_total"] == 0.0


def test_investment_bank_example() -> None:
    """Пример из ТЗ: 1712 ₽ → 38 ₽"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1712}]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 38.0


def test_investment_bank_multiple() -> None:
    """Несколько транзакций"""
    transactions = [
        {"Дата операции": "2024-01-15", "Сумма операции": 1712},
        {"Дата операции": "2024-01-20", "Сумма операции": 548.50},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 39.5


# 2. ТЕСТЫ РАЗНЫХ ЛИМИТОВ
def test_investment_bank_limit_10() -> None:
    """Лимит 10"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1234}]
    result = investment_bank("2024-01", transactions, 10)
    data = json.loads(result)
    assert data["investment_total"] == 6.0


def test_investment_bank_limit_50() -> None:
    """Лимит 50"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1234}]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 16.0


def test_investment_bank_limit_100() -> None:
    """Лимит 100"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1234}]
    result = investment_bank("2024-01", transactions, 100)
    data = json.loads(result)
    assert data["investment_total"] == 66.0


# 3. ТЕСТЫ ФИЛЬТРАЦИИ ПО МЕСЯЦУ
def test_investment_bank_month_filter() -> None:
    """Фильтрация по месяцу"""
    transactions = [
        {"Дата операции": "2024-01-15", "Сумма операции": 1001},
        {"Дата операции": "2024-02-15", "Сумма операции": 2000},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] > 0


def test_investment_bank_month_filter_correct() -> None:
    """Фильтрация по месяцу - правильный тест"""
    transactions = [
        {"Дата операции": "2024-01-15", "Сумма операции": 1001},
        {"Дата операции": "2024-02-15", "Сумма операции": 2001},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    # 1001 → 1050 = 49 ₽
    assert data["investment_total"] == 49.0


def test_investment_bank_wrong_month() -> None:
    """Транзакции не в том месяце"""
    transactions = [
        {"Дата операции": "2024-02-15", "Сумма операции": 1000},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 0.0


# 4. ТЕСТЫ ОШИБОК
def test_investment_bank_invalid_limit() -> None:
    """Некорректный лимит"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1000}]

    with pytest.raises(ValueError, match="Лимит округления должен быть 10, 50 или 100"):
        investment_bank("2024-01", transactions, 75)


def test_investment_bank_invalid_month() -> None:
    """Некорректный месяц"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1000}]

    with pytest.raises(ValueError, match="Месяц должен быть в формате 'YYYY-MM'"):
        investment_bank("2024-13", transactions, 50)


# 5. ТЕСТЫ НЕКОРРЕКТНЫХ ДАННЫХ
def test_investment_bank_empty() -> None:
    """Пустой список транзакций"""
    result = investment_bank("2024-01", [], 50)
    data = json.loads(result)
    assert data["investment_total"] == 0.0


def test_investment_bank_invalid_amount() -> None:
    """Некорректная сумма"""
    transactions: list[dict[str, Any]] = [
        {"Дата операции": "2024-01-01", "Сумма операции": "не число"},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 0.0


def test_investment_bank_missing_fields() -> None:
    """Отсутствуют поля"""
    transactions: list[dict[str, Any]] = [
        {"Дата операции": "2024-01-01"},
        {"Сумма операции": 1000},
    ]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)
    assert data["investment_total"] == 0.0


# 6. ТЕСТ JSON-СТРУКТУРЫ
def test_investment_bank_json_structure() -> None:
    """Проверка структуры JSON"""
    transactions = [{"Дата операции": "2024-01-01", "Сумма операции": 1000}]
    result = investment_bank("2024-01", transactions, 50)
    data = json.loads(result)

    # Обязательные поля
    assert "month" in data
    assert "investment_total" in data
    assert "rounding_limit" in data
    assert "currency" in data

    # Правильные типы
    assert isinstance(data["month"], str)
    assert isinstance(data["investment_total"], (int, float))
    assert isinstance(data["rounding_limit"], int)
    assert data["currency"] == "RUB"
