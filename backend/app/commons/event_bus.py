import pydantic
from typing import Callable


class DomainEvent(pydantic.BaseModel):
    """Base class for all domain events.

    Events represent something that happened in the system. They are
    immutable and published through the event bus for other contexts
    to react to.
    """

    class Config:
        frozen = True


def find_event_class(name: str) -> type | None:
    """Find a DomainEvent subclass by its class name.

    Uses recursive subclass discovery — no manual registration needed.

    Args:
        name: The class name of the event to find.

    Returns:
        The event class, or None if not found.
    """
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
    """In-process event bus that dispatches events to registered handlers."""

    def __init__(self):
        self._handlers: dict[type, list[Callable]] = {}

    def subscribe(self, event_type: type, handler: Callable) -> None:
        """Register a handler for a specific event type."""
        self._handlers.setdefault(event_type, []).append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all registered handlers."""
        for handler in self._handlers.get(type(event), []):
            await handler(event)


event_bus = EventBus()


def event_handler(event_type: type):
    """Decorator that registers a function as a handler for an event type.

    Usage::

        @event_handler(MyEvent)
        async def handle(event: MyEvent) -> None:
            ...

    Args:
        event_type: The DomainEvent subclass to handle.

    Returns:
        A decorator that registers the handler and returns it unchanged.
    """
    def decorator(func: Callable) -> Callable:
        event_bus.subscribe(event_type, func)
        return func
    return decorator
