import fastapi
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "https://wallet-manager.sbapps.dev",
    "http://localhost:5173",
    "http://localhost:4000",
]


def setup_cors(app: fastapi.FastAPI) -> None:
    """Configure CORS middleware on the given FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
