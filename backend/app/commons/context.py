import contextvars
from typing import Any


_user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "user_id", default=None
)


class UserContext:
    """Request-scoped storage for the current authenticated user ID.

    Uses contextvars to maintain per-request state across async calls.
    """

    @staticmethod
    def get() -> str | None:
        """Return the current user ID, or None if not set."""
        return _user_id_ctx.get()

    @staticmethod
    def set(user_id: str) -> contextvars.Token:
        """Set the current user ID for this request context."""
        return _user_id_ctx.set(user_id)

    @staticmethod
    def reset(token: contextvars.Token) -> None:
        """Reset the user ID to its previous value using the given token."""
        _user_id_ctx.reset(token)
