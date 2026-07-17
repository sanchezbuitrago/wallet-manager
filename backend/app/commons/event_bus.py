import pydantic
from typing import Callable


class DomainEvent(pydantic.BaseModel):
    class Config:
        frozen = True


def find_event_class(name: str) -> type | None:
    def get_all_subclasses(cls: type) -> list[type]:
        result = []
        for subclass in cls.__subclasses__():
            result.append(subclass)
            result.extend(get_all_subclasses(subclass))
        return result

    for cls in get_all_subclasses(DomainEvent):
        if cls.__name__ == name:
            return cls
    return None


class EventBus:
    def __init__(self):
        self._handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable):
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: DomainEvent):
        for handler in self._handlers.get(type(event), []):
            await handler(event)


event_bus = EventBus()


def event_handler(event_type: type):
    def decorator(func: Callable) -> Callable:
        event_bus.subscribe(event_type, func)
        return func
    return decorator
