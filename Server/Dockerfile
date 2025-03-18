FROM python:3.12

EXPOSE 8000

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock /app/

WORKDIR /app/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

WORKDIR /app

COPY . .
