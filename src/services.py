import datetime
import json
import logging
from typing import Any, Dict, List

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> str:
    """Рассчитывает сумму для Инвесткопилки за указанный месяц."""
    # Проверка корректности limit
    if limit not in (10, 50, 100):
        logger.error(f"Некорректный лимит округления: {limit}")
        raise ValueError("Лимит округления должен быть 10, 50 или 100")

    # Проверка формата месяца
    try:
        target_date = datetime.datetime.strptime(month, "%Y-%m")
        target_year, target_month = target_date.year, target_date.month
    except ValueError:
        logger.error(f"Некорректный формат месяца: {month}")
        raise ValueError("Месяц должен быть в формате 'YYYY-MM'")

    logger.info(f"Расчет Инвесткопилки для {month} с лимитом {limit}")

    def calculate_rounding_difference(amount: float) -> float:
        """Рассчитывает разницу при округлении до ближайшего limit."""
        if amount % limit == 0:
            return 0.0
        rounded_up = ((amount // limit) + 1) * limit
        return round(rounded_up - amount, 2)

    def is_transaction_in_month(transaction_date: str) -> bool:
        """Проверяет, принадлежит ли транзакция целевому месяцу."""
        try:
            trans_date = datetime.datetime.strptime(transaction_date, "%Y-%m-%d")
            return trans_date.year == target_year and trans_date.month == target_month
        except ValueError:
            logger.warning(f"Некорректный формат даты в транзакции: {transaction_date}")
            return False

    def process_transaction(transaction: Dict[str, Any]) -> float:
        """Обрабатывает одну транзакцию и возвращает сумму для копилки."""
        try:
            # Проверяем, что транзакция в нужном месяце
            if not is_transaction_in_month(transaction.get("Дата операции", "")):
                return 0.0

            # Получаем сумму операции
            amount = transaction.get("Сумма операции", 0)
            if not isinstance(amount, (int, float)):
                logger.warning(f"Некорректная сумма операции: {amount}")
                return 0.0

            # Рассчитываем разницу округления
            return calculate_rounding_difference(abs(amount))
        except Exception as e:
            logger.error(f"Ошибка при обработке транзакции: {e}")
            return 0.0

    # Используем функциональный подход
    rounding_amounts = map(process_transaction, transactions)

    # Суммируем все округления
    total_investment = sum(rounding_amounts)

    logger.info(f"Итоговая сумма для Инвесткопилки: {total_investment:.2f}")

    # Возвращаем JSON-строку как требует ТЗ
    return json.dumps(
        {"month": month, "investment_total": round(total_investment, 2), "rounding_limit": limit, "currency": "RUB"},
        ensure_ascii=False,
    )
