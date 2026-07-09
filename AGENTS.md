# AGENTS.md

## Project Overview

Monorepo with two workspaces:
- `backend/` — FastAPI (Python 3.11) + MongoDB backend. This is where all active code lives.
- `mobile/` — Empty placeholder (no code yet).

## Quick Start (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env-example .env  # then add required vars
uvicorn main:app --reload --port 8000
```

Full stack with Docker:
```bash
cd backend
docker-compose up
```

## Environment Variables

`.env-example` only documents `AUTH_SECRET_KEY`. The app actually requires more (loaded via `pydantic-settings`):

| Variable | Used In | Notes |
|---|---|---|
| `AUTH_SECRET_KEY` | auth entrypoints, wrappers | JWT signing secret |
| `ALGORITHM` | auth entrypoints, wrappers | JWT algorithm, defaults to `HS256` |
| `MONGO_URI` | `commons/adapters/mongo_uow.py` | MongoDB connection string |
| `MONGO_PORT` | `commons/adapters/mongo_uow.py` | MongoDB port |
| `N8N_WEBHOOK` | `webhooks/commons/adapters/n8n/n8n_adapter.py` | n8n webhook URL |
| `REDIS_PASSWORD` | `docker-compose.yml` | For Redis service |

## Architecture

DDD/hexagonal pattern. Each module (`auth`, `webhooks`) follows:

```
<module>/
  domain/
    model/        # Commands, Events, Value Objects, Exceptions
    services/     # Business logic (no I/O)
  entrypoints/    # FastAPI routers
  commons/        # Adapters (DB, external HTTP)
```

Shared infrastructure lives in `backend/app/commons/`:
- `adapters/unit_of_work.py` — Abstract UoW and Repository base classes
- `adapters/mongo_uow.py` — MongoDB implementation
- `adapters/in_memory_uow.py` — In-memory implementation (for dev/testing)
- `wrappers.py` — `@authentication_required` decorator (JWT validation)
- `context.py` — `UserContext` (request-scoped user ID via `contextvars`)
- `standard_types.py` — `ApiResponse`, `ApiError`, `IdGenerator`
- `formatters.py` — `format_http_response()` for consistent JSON envelope

### Routes

| Prefix | Module | File |
|---|---|---|
| `/users` | auth | `app/auth/entrypoints/web.py` |
| `/auth` | auth | `app/auth/entrypoints/web.py` |
| `/webhooks` | webhooks | `app/webhooks/entrypoints/webhooks.py` |

### API Response Shape

All responses use a uniform envelope from `formatters.py`:
```json
{"success": true|false, "body": {}, "errors": []}
```
Validation errors also return HTTP 200 with `success: false` (custom exception handler in `main.py`).

## Database

- **Driver:** `pymongo` (not an ORM — raw MongoDB operations)
- **Unit of Work pattern:** `MongoUOW` → `MongoRepository`, maps entity class name to collection
- **DB name is hardcoded** in `mongo_uow.py` as `buscalibre_scraper` — likely needs changing

## External Integrations

- **Evolution API** (WhatsApp) — credentials hardcoded in `webhooks/commons/adapters/evolution_api.py`
- **n8n** — workflow automation, webhook URL from `N8N_WEBHOOK` env var

## Known Issues

These are real bugs that affect development:

1. ~~`auth/entrypoints/web.py` imports `unit_of_work.FakeUnitOfWork`~~ — fixed, now uses `mongo_uow.MongoUOW()`
2. ~~`commons/adapters/in_memory_uow.py` has broken import~~ — fixed, `from commons import ...` → `from app.commons import ...`
3. Evolution API adapter has hardcoded API key, instance name, and base URL (not env-configurable)
4. MongoDB database name hardcoded as `buscalibre_scraper`
5. `.env-example` is incomplete — missing `ALGORITHM`, `MONGO_URI`, `MONGO_PORT`, `N8N_WEBHOOK`

## Conventions

- Python 3.11, no type checker or linter configured (no mypy, ruff, flake8, pylint)
- No test suite exists — no pytest config, no test files
- No CI/CD workflows
- No pre-commit hooks
- Dependencies managed via `requirements.txt` (no Poetry/Pipenv)
- Logger uses singleton `ColorFormatter` with ANSI colors (`commons/logs.py`)
