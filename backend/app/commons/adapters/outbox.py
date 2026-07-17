from app.commons import base_types
from app.commons import standard_types


class OutboxEventId(base_types.EntityId):
    id: str


class OutboxEvent(base_types.DomainEntity):
    id: OutboxEventId
    event_type: str
    payload: dict
    published: bool = False
    created_at: standard_types.Timestamp
    published_at: standard_types.Timestamp | None = None
    version: int = 1

    @staticmethod
    def create(event_type: str, payload: dict) -> "OutboxEvent":
        return OutboxEvent(
            id=OutboxEventId(id=standard_types.IdGenerator.generate()),
            event_type=event_type,
            payload=payload,
            created_at=standard_types.Timestamp.now()
        )

    def mark_published(self) -> None:
        self.published = True
        self.published_at = standard_types.Timestamp.now()
