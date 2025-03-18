FROM python:3.12

WORKDIR /app

# Установка Poetry
RUN pip install poetry

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock /app/

# Настройка Poetry и установка зависимостей
WORKDIR /app/
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

WORKDIR /app
COPY . .

# Создание и настройка статических файлов
RUN mkdir -p /app/src/static /app/src/media \
  && chmod -R 755 /app/src/static /app/src/media

WORKDIR /app/src
