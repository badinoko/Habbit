# HabitFlow

HabitFlow is a backend-first web application for managing themes, tasks, and habits.

This project is meant to showcase Python backend engineering skills: layered FastAPI architecture, PostgreSQL data modeling, Redis-backed sessions, authentication, CSRF protection, statistics aggregation, scheduled background jobs, and automated testing across multiple levels.

## Backend Highlights

- Layered architecture: `routers -> services -> repositories -> models/schemas`
- Async FastAPI + SQLAlchemy 2.x + PostgreSQL
- Cookie-based auth with Redis-backed session storage
- CSRF protection for state-changing requests
- Owner-scoped access to user data across themes, tasks, habits, and stats
- Habit scheduling engine with multiple recurrence types
- Aggregated statistics page with period-based calculations
- Google OAuth login flow
- Background quote refresh job on application startup and scheduled intervals
- Unit, API-unit, and integration tests
- Strict static checks with Ruff and mypy

## Engineering Problems Solved

### Authentication and Sessions

- Implemented registration, login, logout, and session resolution.
- Stored auth sessions in Redis instead of in-memory state.
- Added optional Google OAuth flow.
- Separated UI session middleware from auth session cookie handling.

### Data Ownership and Security

- Applied owner-scoped data access so users only work with their own records.
- Added CSRF protection for state-changing operations.
- Added rate limiting for auth-related routes.
- Centralized error handling for HTML and JSON responses.

### Domain Logic

- Implemented task priorities and status transitions.
- Built habit scheduling for daily, weekly, monthly, yearly, and interval-based routines.
- Added completion tracking, streak logic, and date-aware filtering.
- Calculated aggregated statistics across tasks, habits, and themes.

### Reliability and Maintainability

- Added Alembic migrations for schema evolution.
- Structured code into clear service and repository boundaries.
- Covered behavior with unit, API-unit, and integration tests.
- Enforced quality gates with Ruff, mypy, and pytest coverage.

## Key Engineering Decisions

- **FastAPI** for explicit request handling, dependency injection, and async support.
- **PostgreSQL** as the primary relational store for application data and reporting queries.
- **Redis** for session-backed authentication state.
- **APScheduler** for lightweight recurring background jobs without adding a queue broker.
- **Layered architecture** to keep transport, business logic, and persistence concerns separated.

## Architecture

```text
Browser
  -> FastAPI routers
     -> services
        -> repositories
           -> PostgreSQL
           -> Redis

APScheduler
  -> services
     -> ZenQuotes API
     -> PostgreSQL
```

### Request Flow

1. Router validates HTTP input and resolves dependencies.
2. Service applies business rules and coordinates use cases.
3. Repository reads or writes PostgreSQL or Redis.
4. Router returns HTML, redirect, or JSON depending on the route.

### Project Structure

```text
.
├── src/
│   ├── routers/        # HTTP and web routes
│   ├── services/       # business logic
│   ├── repositories/   # database and Redis access
│   ├── database/       # SQLAlchemy models and Alembic migrations
│   ├── schemas/        # Pydantic contracts
│   ├── templates/      # Jinja2 templates
│   └── static/         # CSS and JavaScript
├── tests/              # unit, api_unit, integration
├── docs/               # internal contracts and architecture notes
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── .env.example
```

## Product Scope

- Themes with related entity counters
- Tasks with priorities `low`, `medium`, `high`
- Habits with multiple recurrence modes: daily, weekly, monthly, yearly, and interval-based
- Registration, login, logout, and optional Google OAuth
- Server-rendered web UI with FastAPI + Jinja2

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Jinja2
- Vanilla JavaScript
- Poetry
- pytest
- Ruff
- mypy
- Docker
- Docker Compose

## Run

### Option 1. Docker

```bash
git clone https://github.com/Qwertyil/HabitFlow.git
cd HabitFlow
cp .env.example .env
```

Create `.env.docker`:

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
```

Then run:

```bash
make compose-up
make migration
```

Application URL: `http://localhost:8000`
PostgreSQL: `localhost:5430`
Redis: `localhost:6370`

### Option 2. Local Development

Install dependencies:

```bash
poetry install
```

Start infrastructure only:

```bash
docker compose up -d postgres redis
```

Apply migrations:

```bash
poetry run alembic upgrade head
```

Run the app:

```bash
make run
```

Local URL: `http://localhost:8001`

If you use Google OAuth locally, update `GOOGLE_OAUTH_REDIRECT_URI` in `.env` to:

```text
http://localhost:8001/auth/google/callback
```

## Verify

Useful pages:

- `/`
- `/themes`
- `/tasks`
- `/habits`
- `/stats`
- `/auth/login`
- `/auth/register`

Run tests:

```bash
make test
```

Run the main quality checks:

```bash
make lint
make typecheck
make test
```

## Testing Strategy

The test suite is split into three layers:

- `tests/unit` for isolated business logic;
- `tests/api_unit` for route and HTTP behavior;
- `tests/integration` for end-to-end behavior with real infrastructure.

The default `make test` command runs pytest with coverage and enforces a minimum coverage threshold of `80%`.

## Main Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `POSTGRES_DB` | PostgreSQL database name | `mydatabase` |
| `POSTGRES_USER` | PostgreSQL user | `myuser` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `mypassword` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL host port | `5430` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis host port | `6370` |
| `REDIS_PASSWORD` | Redis password | `your_redis_password_here` |
| `REDIS_DB` | Redis DB index | `0` |
| `CONTAINER_APP_PORT` | Docker app port | `8000` |
| `APP_PORT` | local app port | `8001` |
| `UI_SESSION_SECRET_KEY` | UI session middleware secret | `change_me_to_a_long_random_string` |
| `AUTH_SESSION_COOKIE_NAME` | auth cookie name | `auth_session` |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client id | empty |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret | empty |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth callback URL | `http://localhost:8000/auth/google/callback` |
| `ZENQUOTES_API_URL` | quotes provider URL | `https://zenquotes.io/api/quotes` |
| `DEBUG` | debug mode | `True` |

Notes:

- if `DEBUG=False`, `UI_SESSION_SECRET_KEY` must be set explicitly;
- Google OAuth is disabled unless all required `GOOGLE_OAUTH_*` variables are provided;
- `REFILL_INTERVAL_HOURS` exists in config, but the scheduler is currently started with a fixed 6-hour interval in `src/main.py`;
- `Make` is optional because all commands can also be run manually.

## Make Commands

```bash
make run
make test
make lint
make format
make typecheck
make pre-commit
make check
make infra-up
make infra-down
make infra-restart
make infra-logs
make compose-up
make compose-down
make compose-logs
make migration
make psql
```

## Screenshots

<div align="center">
  <img src="assets/main_page.png"
       alt="HabitFlow main page"
       width="800"
       loading="lazy"
       style="border-radius: 12px;
              box-shadow: 0 6px 12px rgba(0,0,0,0.15);
              border: 1px solid #eaeef2;">
  <p><em>Main page</em></p>
</div>

<details>
  <summary>More UI screenshots</summary>

  <div align="center">
    <img src="assets/tasks_list.png"
         alt="Tasks list"
         width="800"
         loading="lazy"
         style="border-radius: 12px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                border: 1px solid #eaeef2;">
    <p><em>Tasks list</em></p>
  </div>

  <div align="center">
    <img src="assets/habits_list.png"
         alt="Habits list"
         width="800"
         loading="lazy"
         style="border-radius: 12px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                border: 1px solid #eaeef2;">
    <p><em>Habits list</em></p>
  </div>

  <div align="center">
    <img src="assets/themes_list.png"
         alt="Themes list"
         width="800"
         loading="lazy"
         style="border-radius: 12px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                border: 1px solid #eaeef2;">
    <p><em>Themes list</em></p>
  </div>
</details>

## Documentation

- `docs/overview.mdc` for project context and architecture principles
- `docs/backend_roadmap.mdc` for roadmap
- `docs/api_contract.mdc` for current HTTP contracts
- `docs/session_contract.mdc` for auth and session behavior
- `docs/testing_strategy.mdc` for testing approach

## Current Status

HabitFlow is an educational backend project with a working web UI, authentication, ownership boundaries, recurring habit logic, statistics, automated tests, and containerized local setup.
