from app.commons import base_types
from app.commons import standard_types


class OutboxEventId(base_types.EntityId):
    id: str


class OutboxEvent(base_types.DomainEntity):
    """Event persisted to the outbox collection before publishing.

    The OutboxWorker polls for unpublished events, publishes them
    through the EventBus, and marks them as published.
    """

    id: OutboxEventId
    event_type: str
    payload: dict
    published: bool = False
    created_at: standard_types.Timestamp
    published_at: standard_types.Timestamp | None = None
    version: int = 1

    @staticmethod
    def create(event_type: str, payload: dict) -> "OutboxEvent":
        """Create a new unpublished outbox event.

        Args:
            event_type: The class name of the DomainEvent.
            payload: The serialized event data.

        Returns:
            A new OutboxEvent ready to be persisted.
        """
        return OutboxEvent(
            id=OutboxEventId(id=standard_types.IdGenerator.generate()),
            event_type=event_type,
            payload=payload,
            created_at=standard_types.Timestamp.now()
        )

    def mark_published(self) -> None:
        """Mark this event as published with the current timestamp."""
        self.published = True
        self.published_at = standard_types.Timestamp.now()
