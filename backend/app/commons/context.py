import contextvars

_user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)

class UserContext:
    @staticmethod
    def get() -> str | None:
        return _user_id_ctx.get()

    @staticmethod
    def set(user_id: str):
        return _user_id_ctx.set(user_id)

    @staticmethod
    def reset(token):
        _user_id_ctx.reset(token)