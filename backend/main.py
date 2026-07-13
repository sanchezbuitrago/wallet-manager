import fastapi
import http
from app.auth.entrypoints import web as auth_entrypoints
from app.webhooks.entrypoints import webhooks as webhooks_entrypoints
from app.analytics.entrypoints import rest as analytics_entrypoints
from app.commons.cors import setup_cors

app = fastapi.FastAPI()

setup_cors(app)

app.include_router(router=webhooks_entrypoints.webhooks_routes, prefix="/webhooks", tags=["Webhooks"])
app.include_router(router=auth_entrypoints.users_routes, prefix="/users", tags=["Users"])
app.include_router(router=auth_entrypoints.auth_routes, prefix="/auth", tags=["Auth"])
app.include_router(router=analytics_entrypoints.analytics_routes, prefix="/analytics", tags=["Analytics"])


@app.exception_handler(fastapi.exceptions.RequestValidationError)
async def validation_exception_handler(request: fastapi.Request, exc: fastapi.exceptions.RequestValidationError):
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
