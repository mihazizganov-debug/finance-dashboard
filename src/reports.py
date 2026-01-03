import datetime
import json
import logging
from typing import Optional

import pandas as pd

# Настройка логирования
logger = logging.getLogger(__name__)


def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> str:
    """Рассчитывает средние траты по дням недели за последние 3 месяца."""
    try:
        logger.info("Запуск отчета 'Траты по дням недели'")

        # Определяем дату для расчета
        if date is None:
            target_date = datetime.datetime.now()
            logger.info(f"Используется текущая дата: {target_date.date()}")
        else:
            try:
                target_date = datetime.datetime.strptime(date, "%Y-%m-%d")
                logger.info(f"Используется переданная дата: {date}")
            except ValueError:
                logger.error(f"Некорректный формат даты: {date}")
                raise ValueError("Дата должна быть в формате 'YYYY-MM-DD'")

        # Проверяем наличие необходимых колонок
        required_columns = ["Дата операции", "Сумма операции"]
        for col in required_columns:
            if col not in transactions.columns:
                logger.error(f"Отсутствует обязательная колонка: {col}")
                raise ValueError(f"DataFrame должен содержать колонку '{col}'")

        # Копируем DataFrame чтобы не изменять оригинал
        df = transactions.copy()

        # Преобразуем дату в datetime если это еще не сделано
        if not pd.api.types.is_datetime64_any_dtype(df["Дата операции"]):
            df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

        # Вычисляем дату 3 месяца назад
        three_months_ago = target_date - datetime.timedelta(days=90)

        # Фильтруем транзакции за последние 3 месяца
        mask = (df["Дата операции"] >= three_months_ago) & (df["Дата операции"] <= target_date)
        recent_transactions = df[mask].copy()

        if recent_transactions.empty:
            logger.warning("Нет транзакций за последние 3 месяца")
            # Возвращаем нулевые значения для всех дней недели
            days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            result_dict = {day: 0.0 for day in days_of_week}

            return json.dumps(
                {
                    "report": "spending_by_weekday",
                    "period": f"{three_months_ago.date()} - {target_date.date()}",
                    "data": result_dict,
                    "status": "success",
                    "message": "Нет транзакций за указанный период",
                },
                ensure_ascii=False,
            )

        # Добавляем колонку с днем недели
        # 0 = понедельник, 6 = воскресенье
        recent_transactions["День недели"] = recent_transactions["Дата операции"].dt.dayofweek
        recent_transactions["День недели название"] = recent_transactions["Дата операции"].dt.day_name()

        # Группируем по дню недели и считаем средние траты
        # Берем абсолютное значение сумм (траты положительные)
        recent_transactions["Абсолютная сумма"] = recent_transactions["Сумма операции"].abs()
        weekday_stats = recent_transactions.groupby("День недели название")["Абсолютная сумма"].mean()

        # Создаем результат с правильным порядком дней
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_russian = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

        result_dict = {}
        for eng_day, rus_day in zip(days_order, days_russian):
            if eng_day in weekday_stats.index:
                result_dict[rus_day] = round(float(weekday_stats[eng_day]), 2)
            else:
                result_dict[rus_day] = 0.0

        # Логируем результат
        logger.info(
            f"Рассчитаны средние траты по дням недели за период: " f"{three_months_ago.date()} - {target_date.date()}"
        )

        # Возвращаем JSON
        return json.dumps(
            {
                "report": "spending_by_weekday",
                "period": {"start": three_months_ago.strftime("%Y-%m-%d"), "end": target_date.strftime("%Y-%m-%d")},
                "data": result_dict,
                "status": "success",
                "total_days": len(recent_transactions),
                "average_daily": round(float(recent_transactions["Абсолютная сумма"].mean()), 2),
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"Ошибка в функции spending_by_weekday: {str(e)}")
        return json.dumps(
            {"report": "spending_by_weekday", "status": "error", "error": str(e)}, ensure_ascii=False, indent=2
        )
