import abc
from app.commons.adapters import outbox


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, item) -> None:
        ...

    @abc.abstractmethod
    def find_by_id(self, entity_id):
        ...

    @abc.abstractmethod
    def find_by(self, find: dict, sort_by: str = "created_at", descending: bool = True):
        ...

    @abc.abstractmethod
    def get_all(self, descending: bool = True, limit: int = 20, sort_by: str = "created_at"):
        ...


class AbstractUnitOfWork(abc.ABC):
    def __init__(self):
        self._events: list = []
        self._in_transaction: bool = False
        self.session = None

    def get_repo(self, entity_type: type):
        return self._create_repo(entity_type)

    @abc.abstractmethod
    def _create_repo(self, entity_type: type) -> AbstractRepository:
        ...

    def add_event(self, event) -> None:
        self._events.append(event)
        if not self._in_transaction:
            self._persist_events_to_outbox()

    def _persist_events_to_outbox(self) -> None:
        outbox_repo = self._create_repo(outbox.OutboxEvent)
        for event in self._events:
            outbox_event = outbox.OutboxEvent.create(
                event_type=type(event).__name__,
                payload=event.dict()
            )
            outbox_repo.save(outbox_event)
        self._events.clear()

    def transaction(self):
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
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    async def __aenter__(self):
        self._uow._in_transaction = True
        await self._uow._start_transaction()
        return self._uow

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            outbox_repo = self._uow._create_repo(outbox.OutboxEvent)
            for event in self._uow._events:
                outbox_event = outbox.OutboxEvent.create(
                    event_type=type(event).__name__,
                    payload=event.dict()
                )
                outbox_repo.save(outbox_event)
            await self._uow._commit_transaction()
            self._uow._events.clear()
        else:
            await self._uow._abort_transaction()
        self._uow._in_transaction = False
        return False
