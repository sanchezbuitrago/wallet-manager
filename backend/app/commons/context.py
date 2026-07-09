from contextvars import ContextVar
from typing import Optional

_user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)

class UserContext:
    @staticmethod
    def get() -> Optional[str]:
        return _user_id_ctx.get()

    @staticmethod
    def set(user_id: str):
        return _user_id_ctx.set(user_id)

    @staticmethod
    def reset(token):
        _user_id_ctx.reset(token)