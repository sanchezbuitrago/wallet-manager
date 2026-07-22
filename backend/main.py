import asyncio
import http
from contextlib import asynccontextmanager

import fastapi

from app.commons.adapters import outbox_worker
from app.commons.cors import setup_cors
from app.webhooks.entrypoints import webhooks as webhooks_entrypoints
from app.auth.entrypoints.web import auth_routes
from app.auth.entrypoints.web import users_routes
from app.admin.entrypoints.web import admin_routes
from app.analytics.entrypoints.rest import analytics_routes

# Side-effect imports: registering handlers must happen before the app starts.
import app.webhooks.entrypoints.events  # noqa: E402
import app.account.entrypoints.events  # noqa: E402
import app.notification.entrypoints.events  # noqa: E402

worker = outbox_worker.OutboxWorker(interval=5.0)


@asynccontextmanager
async def lifespan(fastapi_app: fastapi.FastAPI):
    """Application lifespan: start the outbox worker on startup."""
    asyncio.create_task(worker.start())
    yield
    worker.stop()


application = fastapi.FastAPI(lifespan=lifespan)
setup_cors(application)

application.include_router(
    router=webhooks_entrypoints.webhooks_routes,
    prefix="/webhooks",
    tags=["Webhooks"]
)

application.include_router(
    router=auth_routes,
    prefix="/auth",
    tags=["Auth"]
)

application.include_router(
    router=users_routes,
    prefix="/users",
    tags=["Users"]
)

application.include_router(
    router=admin_routes,
    prefix="/admin",
    tags=["Admin"]
)

application.include_router(
    router=analytics_routes,
    prefix="/analytics",
    tags=["Analytics"]
)


@application.exception_handler(fastapi.exceptions.RequestValidationError)
async def validation_exception_handler(
    request: fastapi.Request,
    exc: fastapi.exceptions.RequestValidationError,
):
    """Return validation errors in the standard API envelope format."""
    errors = exc.errors()
    return fastapi.responses.JSONResponse(
        status_code=http.HTTPStatus.OK,
        content={
            "success": False,
            "body": {},
            "errors": [
                {
                    "title": "Bad Request",
                    "code": "exception/RequestFormatError",
                    "detail": (
                        f"{error.get('msg')} "
                        f"[{'.'.join(error.get('loc', []))}]"
                    )
                } for error in errors
            ]
        }
    )
