import json
import os
import sys

import pandas as pd

from src.reports import spending_by_weekday


def create_test_dataframe() -> pd.DataFrame:
    """Создает тестовый DataFrame"""
    data = {
        "Дата операции": pd.date_range("2024-01-01", periods=30, freq="D"),
        "Сумма операции": [100 + i * 10 for i in range(30)],
        "Категория": ["Транзакция"] * 30,
        "Описание": ["Тест"] * 30,
    }
    return pd.DataFrame(data)


def test_spending_by_weekday_basic() -> None:
    """Базовый тест функции"""
    df = create_test_dataframe()
    result = spending_by_weekday(df, "2024-02-01")
    data = json.loads(result)

    assert data["status"] == "success"
    assert "data" in data
    assert "Понедельник" in data["data"]


def test_spending_by_weekday_no_date() -> None:
    """Тест без указания даты (используется текущая)"""
    df = create_test_dataframe()
    result = spending_by_weekday(df)
    data = json.loads(result)

    assert data["status"] == "success"
    assert "period" in data


def test_spending_by_weekday_empty_data() -> None:
    """Тест с пустым DataFrame"""
    df = pd.DataFrame(columns=["Дата операции", "Сумма операции"])
    result = spending_by_weekday(df, "2024-01-01")
    data = json.loads(result)

    assert data["status"] == "success"
    assert data["message"] == "Нет транзакций за указанный период"


def test_spending_by_weekday_missing_columns() -> None:
    """Тест с отсутствующими колонками"""
    df = pd.DataFrame({"Неправильная колонка": [1, 2, 3]})
    result = spending_by_weekday(df, "2024-01-01")
    data = json.loads(result)

    # Функция возвращает JSON с ошибкой, а не вызывает исключение
    assert data["status"] == "error"
    assert "error" in data
    assert "DataFrame должен содержать колонку" in data["error"]


def test_spending_by_weekday_invalid_date() -> None:
    """Тест с некорректной датой"""
    df = create_test_dataframe()
    result = spending_by_weekday(df, "2024-13-01")
    data = json.loads(result)

    # Функция возвращает JSON с ошибкой, а не вызывает исключение
    assert data["status"] == "error"
    assert "error" in data
    assert "Дата должна быть в формате" in data["error"]


def test_spending_by_weekday_json_structure() -> None:
    """Тест структуры JSON-ответа"""
    df = create_test_dataframe()
    result = spending_by_weekday(df, "2024-02-01")
    data = json.loads(result)

    required_fields = ["report", "period", "data", "status"]
    for field in required_fields:
        assert field in data

    # Проверяем дни недели
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    for day in days:
        assert day in data["data"]
        assert isinstance(data["data"][day], (int, float))
