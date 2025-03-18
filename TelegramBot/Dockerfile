FROM python:3.12-slim

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock* /app/

# Настройка Poetry и установка зависимостей
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Копируем код бота
COPY . .

# Создаем директорию для логов
RUN mkdir -p logs

# Запускаем бота
CMD ["python", "main.py"] 