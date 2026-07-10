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

All required variables are documented in `.env-example` (loaded via `pydantic-settings`):

| Variable | Used In | Notes |
|---|---|---|
| `AUTH_SECRET_KEY` | auth entrypoints, wrappers | JWT signing secret |
| `ALGORITHM` | auth entrypoints, wrappers | JWT algorithm, defaults to `HS256` |
| `MONGO_URI` | `commons/adapters/mongo_uow.py` | MongoDB connection string |
| `MONGO_PORT` | `commons/adapters/mongo_uow.py` | MongoDB port |
| `MONGO_DB_NAME` | `commons/adapters/mongo_uow.py` | MongoDB database name, defaults to `WalletManager` |
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
- `base_types.py` — `ValueObject`, `EntityId`, `DomainEntity`, `Aggregate`, `ForeignAggregate`

### Aggregate Ownership

Each context owns its aggregates. Cross-context references use `ForeignAggregate` (a lightweight entity with only `id`):

| Context | Aggregate | Location |
|---|---|---|
| `auth` | `User` (full lifecycle) | `app/auth/domain/model/aggregates.py` |
| `webhooks` | `Message` | `app/webhooks/domain/model/aggregates.py` |
| `webhooks` | `User` (FK reference only) | `app/webhooks/domain/model/entities.py` |

### Module Independence Rule

Modules (`auth`, `webhooks`, or any future module) must **never import from each other**. All shared logic (models, services, adapters) must live in `commons/`. This keeps modules decoupled and ready for future microservice extraction.

When a module needs to query data owned by another context, it uses the UoW pattern with its own `ForeignAggregate` entity to query the collection directly — no service imports between modules.

```
  <module_a> ──→ commons (shared)
  <module_b> ──→ commons (shared)

  <module_a> ──✗──→ <module_b>  # FORBIDDEN
  <module_b> ──✗──→ <module_a>  # FORBIDDEN
```

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
- **DB name** configurable via `MONGO_DB_NAME` env var, defaults to `WalletManager`

## External Integrations

- **Evolution API** (WhatsApp) — credentials hardcoded in `webhooks/commons/adapters/evolution_api.py`
- **n8n** — workflow automation, webhook URL from `N8N_WEBHOOK` env var

## Known Issues

These are real bugs that affect development:

1. ~~`auth/entrypoints/web.py` imports `unit_of_work.FakeUnitOfWork`~~ — fixed, now uses `mongo_uow.MongoUOW()`
2. ~~`commons/adapters/in_memory_uow.py` has broken import~~ — fixed, `from commons import ...` → `from app.commons import ...`
3. Evolution API adapter has hardcoded API key, instance name, and base URL (not env-configurable)
4. ~~MongoDB database name hardcoded as `buscalibre_scraper`~~ — fixed, now configurable via `MONGO_DB_NAME` env var
5. ~~`.env-example` is incomplete~~ — fixed, now documents all required env vars

## Conventions

- Python 3.11, no type checker or linter configured (no mypy, ruff, flake8, pylint)
- No test suite exists — no pytest config, no test files
- No CI/CD workflows
- No pre-commit hooks
- Dependencies managed via `requirements.txt` (no Poetry/Pipenv)
- Logger uses singleton `ColorFormatter` with ANSI colors (`commons/logs.py`)
