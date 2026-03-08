# HabitFlow

HabitFlow — веб-приложение для управления задачами, привычками и пользовательскими сессиями.

Проект развивается в формате **web-first**:
- основной интерфейс — серверные веб-роуты (`HTML + Redirect + AJAX JSON`);
- JSON API под `/api/*` — дополнительный слой.

<div align="center">
  <img src="assets/main_page.png"
       alt="Главная страница"
       width="800"
       loading="lazy"
       style="border-radius: 12px;
              box-shadow: 0 6px 12px rgba(0,0,0,0.15);
              border: 1px solid #eaeef2;">
  <p><em>Главная страница</em></p>
</div>
<div align="center">
  <img src="assets/tasks_list.png"
       alt="Список задач"
       width="800"
       loading="lazy"
       style="border-radius: 12px;
              box-shadow: 0 6px 12px rgba(0,0,0,0.15);
              border: 1px solid #eaeef2;">
  <p><em>Страница со списком задач</em></p>
</div>
<div align="center">
  <img src="assets/habits_list.png"
       alt="Список привычек"
       width="800"
       loading="lazy"
       style="border-radius: 12px;
              box-shadow: 0 6px 12px rgba(0,0,0,0.15);
              border: 1px solid #eaeef2;">
  <p><em>Страница со списком привычек</em></p>
</div>
<div align="center">
  <img src="assets/themes_list.png"
       alt="Список тем"
       width="800"
       loading="lazy"
       style="border-radius: 12px;
              box-shadow: 0 6px 12px rgba(0,0,0,0.15);
              border: 1px solid #eaeef2;">
  <p><em>Страница с темами</em></p>
</div>

## Стек технологий

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic
- **Хранилища**: PostgreSQL (asyncpg), Redis (хранилище auth-сессий)
- **Фронтенд**: Jinja2, HTML, CSS, JavaScript
- **Инфраструктура**: Docker, Docker Compose
- **Инструменты**: Poetry, pre-commit, Ruff, mypy, pytest

## Структура проекта

```text
.
├── docker-compose.yml         # Запуск app + postgres + redis
├── Dockerfile                 # Сборка образа приложения
├── Makefile                   # Команды разработки
├── .env.example               # Пример переменных для локального запуска
├── .env.docker.example        # Переопределения env для app-контейнера
├── docs/                      # Проектная документация
│   ├── overview.mdc
│   ├── backend_roadmap.mdc
│   ├── api_contract.mdc
│   ├── session_contract.mdc
│   └── testing_strategy.mdc
├── src/                       # Исходный код приложения
└── tests/                     # Тесты
```

## Требования

- **Python** 3.12+
- **Poetry**
- **Docker** и **Docker Compose**
- **Make** (опционально)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Qwertyil/HabitFlow.git
cd HabitFlow
```

### 2. Подготовка переменных окружения

```bash
cp .env.example .env
cp .env.docker.example .env.docker
```

- `.env` используется локальным запуском (например, `POSTGRES_HOST=localhost`, `REDIS_HOST=localhost`).
- `.env.docker` подмешивается в `app`-контейнер и переопределяет хосты для сети compose (`postgres`, `redis`).

### 3. Запуск через Docker (рекомендуется)

```bash
make restart
# или вручную
docker compose up -d --build
```

Поднимутся сервисы: `app`, `postgres`, `redis`.

### 4. Миграции

```bash
make migration
# или вручную
docker compose exec app alembic upgrade head
```

### 5. Проверка

Приложение доступно на `http://localhost:8000` (порт задаётся `CONTAINER_APP_PORT`, по умолчанию `8000`).

## Локальный запуск (без app-контейнера)

1. Установить зависимости:

```bash
poetry install
```

2. Поднять только инфраструктуру:

```bash
docker compose up -d postgres redis
```

3. Применить миграции локально:

```bash
poetry run alembic upgrade head
```

4. Запустить приложение:

```bash
make run
# или вручную
poetry run uvicorn src.main:app --reload --port 8001
```

Приложение будет доступно на `http://localhost:8001` (порт из `APP_PORT`).

## Команды Makefile

- `make run` — локальный запуск FastAPI (uvicorn + reload).
- `make test` — запуск тестов.
- `make lint` — проверка Ruff.
- `make format` — форматирование Ruff + autofix.
- `make typecheck` — проверка mypy.
- `make pre-commit` — запуск pre-commit.
- `make check` — format + lint + typecheck + test.
- `make restart` — пересобрать и поднять контейнеры.
- `make migration` — применить миграции в app-контейнере.
- `make psql` — подключиться к PostgreSQL в контейнере.

## Тестирование

```bash
make test
```

или:

```bash
poetry run pytest -v
```

Основные группы тестов:
- `tests/unit`
- `tests/api_unit`
- `tests/integration`

## Документация

- `docs/overview.mdc` — контекст проекта и принципы.
- `docs/backend_roadmap.mdc` — план итераций.
- `docs/api_contract.mdc` — web/API-контракты.
- `docs/session_contract.mdc` — контракт auth/session.
- `docs/testing_strategy.mdc` — стратегия тестирования.

## Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|---|---|---|
| POSTGRES_DB | Имя БД PostgreSQL | mydatabase |
| POSTGRES_USER | Пользователь PostgreSQL | myuser |
| POSTGRES_PASSWORD | Пароль PostgreSQL | mypassword |
| POSTGRES_HOST | Хост PostgreSQL | localhost |
| POSTGRES_PORT | Порт PostgreSQL | 5432 |
| REDIS_HOST | Хост Redis | localhost |
| REDIS_PORT | Порт Redis | 6379 |
| REDIS_PASSWORD | Пароль Redis | your_redis_password_here |
| REDIS_DB | База Redis | 0 |
| CONTAINER_APP_PORT | Порт app в Docker | 8000 |
| APP_PORT | Порт локального uvicorn | 8001 |
| UI_SESSION_SECRET_KEY | Секрет UI-сессий | change_me_to_a_long_random_string |
| UI_SESSION_COOKIE_NAME | Имя cookie UI-сессии | habitflow_session |
| UI_SESSION_MAX_AGE | TTL UI-сессии (сек.) | 1209600 |
| UI_SESSION_SAME_SITE | SameSite UI-cookie | lax |
| UI_SESSION_HTTPS_ONLY | `Secure` для UI-cookie | False |
| AUTH_SESSION_COOKIE_NAME | Имя cookie auth-сессии | auth_session |
| AUTH_SESSION_MAX_AGE | TTL auth-сессии (сек.) | 1209600 |
| AUTH_SESSION_SAME_SITE | SameSite auth-cookie | lax |
| AUTH_SESSION_HTTPS_ONLY | `Secure` для auth-cookie | False |
| API_KEY | Технический ключ приложения | your_api_key_here |
| DEBUG | Режим отладки | True |

> Если `DEBUG=False`, `UI_SESSION_SECRET_KEY` должен быть задан явно.
