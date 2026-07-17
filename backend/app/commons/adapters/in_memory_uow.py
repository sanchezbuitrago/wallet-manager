from app.commons import base_types
from app.commons.adapters import unit_of_work


class InMemoryRepository(unit_of_work.AbstractRepository):
    """In-memory repository for unit testing."""

    def __init__(self, entity_type: type, store: dict, uow=None):
        self._entity_type = entity_type
        self._store = store
        self._uow = uow

    def save(self, item: base_types.Aggregate) -> None:
        """Insert or update an entity with optimistic locking."""
        self._assert_not_readonly(item)
        key = item.id.key()
        existing = self._store.get(key)

        if existing:
            expected_version = item.version
            if existing.version != expected_version:
                raise base_types.OptimisticLockError(
                    f"Entity [{key}] was modified by another process"
                )
            item.version = expected_version + 1
            self._store[key] = item
        else:
            self._store[key] = item

    def find_by_id(self, entity_id: base_types.EntityId) -> base_types.Aggregate | None:
        """Find a single entity by its ID."""
        return self._store.get(entity_id.key())

    def find_by(self, find: dict, sort_by: str = "created_at", descending: bool = True):
        """Query entities matching the given filter."""
        results = list(self._store.values())
        for field, value in find.items():
            results = [r for r in results if getattr(r, field, None) == value]

        def sort_key(item):
            val = getattr(item, sort_by, None)
            if val is None:
                return ""
            if hasattr(val, "value"):
                return val.value
            return str(val)

        results.sort(key=sort_key, reverse=descending)
        return iter(results)

    def get_all(self, descending: bool = True, limit: int = 20, sort_by: str = "created_at"):
        """Return all entities with sorting and pagination."""
        results = list(self._store.values())

        def sort_key(item):
            val = getattr(item, sort_by, None)
            if val is None:
                return ""
            if hasattr(val, "value"):
                return val.value
            return str(val)

        results.sort(key=sort_key, reverse=descending)
        return iter(results[:limit])

    def _assert_not_readonly(self, item: base_types.DomainEntity) -> None:
        if isinstance(item, base_types.ForeignAggregate):
            raise TypeError(
                f"Cannot save read-only entity [{item.id.key()}]"
            )


class InMemoryUOW(unit_of_work.AbstractUnitOfWork):
    """In-memory unit of work for unit testing.

    Mirrors the behavioral contract of MongoUOW without external
    dependencies. Supports transactions via snapshot/restore.
    """

    def __init__(self):
        super().__init__()
        self._stores: dict[type, dict] = {}

    def _get_store(self, entity_type: type) -> dict:
        if entity_type not in self._stores:
            self._stores[entity_type] = {}
        return self._stores[entity_type]

    def _create_repo(self, entity_type: type) -> InMemoryRepository:
        return InMemoryRepository(
            entity_type=entity_type,
            store=self._get_store(entity_type),
            uow=self
        )

    async def _start_transaction(self) -> None:
        self._snapshot = {
            et: dict(store) for et, store in self._stores.items()
        }

    async def _commit_transaction(self) -> None:
        self._snapshot = None

    async def _abort_transaction(self) -> None:
        self._stores = self._snapshot
        self._snapshot = None
