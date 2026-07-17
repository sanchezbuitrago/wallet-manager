import abc
import traceback
from typing import Any

from app.commons.adapters import outbox


class AbstractRepository(abc.ABC):
    """Base class for all repository implementations."""

    @abc.abstractmethod
    def save(self, item: Any) -> None:
        """Persist an entity (insert or update)."""
        ...

    @abc.abstractmethod
    def find_by_id(self, entity_id: Any) -> Any | None:
        """Retrieve a single entity by its ID."""
        ...

    @abc.abstractmethod
    def find_by(self, find: dict, sort_by: str = "created_at", descending: bool = True) -> Any:
        """Query entities matching the given filter."""
        ...

    @abc.abstractmethod
    def get_all(self, descending: bool = True, limit: int = 20, sort_by: str = "created_at") -> Any:
        """Return all entities with sorting and pagination."""
        ...


class AbstractUnitOfWork(abc.ABC):
    """Base class for unit-of-work implementations.

    Manages transaction boundaries and an outbox-style event list.
    Events are persisted to the outbox on commit (if inside a
    transaction) or immediately (if outside a transaction).
    """

    def __init__(self):
        self._events: list = []
        self._in_transaction: bool = False
        self.session = None

    def get_repo(self, entity_type: type) -> AbstractRepository:
        """Return a repository for the given entity type."""
        return self._create_repo(entity_type)

    @abc.abstractmethod
    def _create_repo(self, entity_type: type) -> AbstractRepository:
        ...

    def add_event(self, event: Any) -> None:
        """Queue a domain event for publishing.

        If inside a transaction the event is held in memory until commit.
        If outside a transaction it is persisted to the outbox immediately.
        """
        self._events.append(event)
        if not self._in_transaction:
            self._persist_events_to_outbox()

    def _persist_events_to_outbox(self) -> None:
        """Write all pending events to the outbox collection."""
        outbox_repo = self._create_repo(outbox.OutboxEvent)
        for event in self._events:
            outbox_event = outbox.OutboxEvent.create(
                event_type=type(event).__name__,
                payload=event.model_dump()
            )
            outbox_repo.save(outbox_event)
        self._events.clear()

    def transaction(self) -> "_TransactionContext":
        """Return an async context manager that wraps a transaction."""
        return _TransactionContext(self)

    @abc.abstractmethod
    async def _start_transaction(self) -> None:
        ...

    @abc.abstractmethod
    async def _commit_transaction(self) -> None:
        ...

    @abc.abstractmethod
    async def _abort_transaction(self) -> None:
        ...


class _TransactionContext:
    """Async context manager that wraps a UoW transaction.

    On enter, starts a MongoDB session/transaction.
    On exit, commits (and flushes events to outbox) or aborts on error.
    """

    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __aenter__(self) -> AbstractUnitOfWork:
        self._uow._in_transaction = True
        await self._uow._start_transaction()
        return self._uow

    async def __aexit__(
        self,
        exc_type: type | None,
        exc_val: BaseException | None,
        exc_tb: traceback.TracebackType | None,
    ) -> bool:
        if exc_type is None:
            outbox_repo = self._uow._create_repo(outbox.OutboxEvent)
            for event in self._uow._events:
                outbox_event = outbox.OutboxEvent.create(
                    event_type=type(event).__name__,
                    payload=event.model_dump()
                )
                outbox_repo.save(outbox_event)
            await self._uow._commit_transaction()
            self._uow._events.clear()
        else:
            await self._uow._abort_transaction()
        self._uow._in_transaction = False
        return False
