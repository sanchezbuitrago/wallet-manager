import asyncio
from contextlib import asynccontextmanager

import fastapi

from app.commons.adapters import outbox_worker
from app.commons.cors import setup_cors
from app.webhooks.entrypoints import webhooks as webhooks_entrypoints
from app.auth.entrypoints.web import auth_routes, users_routes
from app.analytics.entrypoints.rest import analytics_routes

# Import event handlers to register them with the event bus
import app.webhooks.entrypoints.events  # noqa: E402
import app.account.entrypoints.events  # noqa: E402
import app.notification.entrypoints.events  # noqa: E402

worker = outbox_worker.OutboxWorker(interval=5.0)


@asynccontextmanager
async def lifespan(fastapi_app: fastapi.FastAPI):
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
    router=analytics_routes,
    prefix="/analytics",
    tags=["Analytics"]
)


@application.exception_handler(fastapi.exceptions.RequestValidationError)
async def validation_exception_handler(
    request: fastapi.Request,
    exc: fastapi.exceptions.RequestValidationError
):
    import http
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
                    "detail": f"{error.get('msg')} [{'.'.join(error.get('loc', []))}]"
                } for error in errors
            ]
        }
    )
