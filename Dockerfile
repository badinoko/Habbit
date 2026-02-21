FROM python:3.12.3-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
ENV POETRY_VERSION=2.1.3
RUN pip install "poetry==$POETRY_VERSION"

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock* README.md ./

# Устанавливаем зависимости
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --without dev

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
