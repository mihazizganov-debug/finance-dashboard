# 🏦 Finance Dashboard

**Курсовой проект** | Python-разработка | Skypro  
Дашборд для анализа банковских транзакций с генерацией JSON и Excel-отчетов.

## 🚀 Функционал
- Загрузка и анализ транзакций из Excel
- Интеграция с API курсов валют и биржевых данных
- Автоматические отчеты в JSON и Excel форматах
- Расчет статистики по картам и кешбэка

## 🛠 Технологии
- **Backend**: Python 3.10+
- **Тестирование**: pytest (85% coverage)
- **CI/CD**: GitHub Actions
- **Качество кода**: flake8, black
- **Менеджмент зависимостей**: Poetry
- **Логирование**: стандартная библиотека logging

## 📊 Архитектура

src/
├── utils.py # Бизнес-логика
├── views.py # Представление
└── init.py

tests/
├── test_utils.py
└── test_views.py

## 🏃‍♂️ Запуск
```bash
poetry install
poetry run python main.py

🧪 Тестирование
# Запуск тестов с отчетом о покрытии
poetry run pytest --cov=src --cov-report=html

# Для просмотра отчета в терминале
poetry run pytest --cov=src --cov-report=term

## 🚀 Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/[твой-username]/finance-dashboard.git
cd finance-dashboard

# Установка зависимостей
poetry install

# Запуск приложения
poetry run python main.py
