import json
from typing import Any

import pymongo
import pydantic_settings

from app.commons import base_types
from app.commons import logs
from app.commons.adapters import unit_of_work

_LOGGER = logs.get_logger()


class _Settings(pydantic_settings.BaseSettings):
    mongo_uri: str
    mongo_port: str
    mongo_db_name: str = "WalletManager"


_SETTINGS = _Settings()
_client: pymongo.MongoClient | None = None


def _get_client() -> pymongo.MongoClient:
    global _client
    if _client is None:
        _client = pymongo.MongoClient(
            f"mongodb://{_SETTINGS.mongo_uri}:{_SETTINGS.mongo_port}/"
        )
    return _client


class MongoUOW(unit_of_work.AbstractUnitOfWork):
    """MongoDB-backed unit of work with transaction support."""

    def __init__(self):
        super().__init__()
        self.client = _get_client()

    def _create_repo(self, entity_type: type) -> "MongoRepository":
        return MongoRepository(
            entity_type=entity_type,
            db_client=self.client,
            uow=self
        )

    async def _start_transaction(self) -> None:
        self.session = self.client.start_session()
        self.session.start_transaction()

    async def _commit_transaction(self) -> None:
        self.session.commit_transaction()
        self.session.end_session()
        self.session = None

    async def _abort_transaction(self) -> None:
        self.session.abort_transaction()
        self.session.end_session()
        self.session = None


class MongoRepository(unit_of_work.AbstractRepository):
    """Repository implementation backed by a MongoDB collection."""

    def __init__(
        self,
        entity_type: type,
        db_client: pymongo.MongoClient,
        uow: MongoUOW | None = None,
    ):
        self._entity_type = entity_type
        self.db = db_client[_SETTINGS.mongo_db_name]
        self.collection = self.db[entity_type.__name__]
        self._uow = uow

    @property
    def session(self) -> Any:
        """Return the active MongoDB session, or None."""
        return self._uow.session if self._uow else None

    def get_model_type(self) -> type:
        """Return the entity type this repository manages."""
        return self._entity_type

    def save(self, new_item: base_types.Aggregate) -> None:
        """Insert or update an entity with optimistic locking."""
        self._assert_not_readonly(new_item)
        doc = self._parse_to_mongo_document(new_item)
        existing = self.collection.find_one(
            {"_id": new_item.id.key()},
            session=self.session
        )
        if existing:
            expected_version = new_item.version
            new_item.version = expected_version + 1
            result = self.collection.update_one(
                filter={"_id": new_item.id.key(), "version": expected_version},
                update={"$set": doc},
                session=self.session,
            )
            if result.matched_count == 0:
                raise base_types.OptimisticLockError(
                    f"Entity [{new_item.id.key()}] was modified by another process"
                )
        else:
            self.collection.insert_one(doc, session=self.session)

    def _assert_not_readonly(self, item: base_types.DomainEntity) -> None:
        if isinstance(item, base_types.ForeignAggregate):
            raise TypeError(
                f"Cannot save read-only entity [{item.id.key()}]"
            )

    def find_by_id(self, entity_id: base_types.EntityId) -> Any | None:
        """Find a single entity by its ID."""
        cursor = self.collection.find(
            {"_id": entity_id.key()},
            session=self.session
        )
        document = next(cursor, None)
        return self._entity_type.model_validate(document) if document else None

    def find_by(
        self,
        find: dict,
        sort_by: str = "created_at",
        descending: bool = True
    ) -> Any:
        """Query entities matching the given filter."""
        all_documents = self.collection.find(
            find, session=self.session
        ).sort(
            sort_by,
            pymongo.DESCENDING if descending else pymongo.ASCENDING
        )
        for document in all_documents:
            yield self._entity_type.model_validate(document)

    def get_all(
        self,
        descending: bool = True,
        limit: int = 20,
        sort_by: str = "created_at"
    ) -> Any:
        """Return all entities with sorting and pagination."""
        all_documents = self.collection.find(
            session=self.session
        ).sort(
            sort_by,
            pymongo.DESCENDING if descending else pymongo.ASCENDING
        ).limit(limit=limit)
        for document in all_documents:
            yield self._entity_type.model_validate(document)

    def _parse_to_mongo_document(self, item: base_types.Aggregate) -> dict[str, Any]:
        """Serialize an entity to a MongoDB document dict."""
        new_item = json.loads(item.model_dump_json())
        new_item.update({"_id": item.id.key()})
        return new_item
