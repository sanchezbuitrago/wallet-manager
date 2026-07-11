import json
from typing import Any, Iterator

import pymongo
import pydantic_settings

from app.commons import base_types, logs
from app.commons.adapters import unit_of_work

_LOGGER = logs.get_logger()

class _Settings(pydantic_settings.BaseSettings):
    mongo_uri: str
    mongo_port: str
    mongo_db_name: str = "WalletManager"

_SETTINGS = _Settings()


class MongoUOW(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:

        self.client: pymongo.MongoClient = pymongo.MongoClient(
            f"mongodb://{_SETTINGS.mongo_uri}:{_SETTINGS.mongo_port}/"
        )

    def get_repo(
        self, entity_type: type[unit_of_work.T]
    ) -> unit_of_work.AbstractRepository[unit_of_work.T]:
        return MongoRepository(entity_type=entity_type, db_client=self.client)


class MongoRepository(unit_of_work.AbstractRepository):
    def __init__(
        self, entity_type: type[unit_of_work.T], db_client: pymongo.MongoClient
    ) -> None:
        self._entity_type: type[unit_of_work.T] = entity_type
        self.db_client: pymongo.MongoClient = db_client
        self.db: pymongo.collection.Database = db_client[_SETTINGS.mongo_db_name]
        self.collection = self._get_collection()

    def get_model_type(self) -> type[unit_of_work.T]:
        return self._entity_type

    def query(self) -> Iterator[unit_of_work.T]:
        raise NotImplementedError()

    def find_by(self, find: dict[str, str], sort_by: str = "created_at", descending: bool = True) -> Iterator[
        unit_of_work.T]:
        all_documents = self.collection.find(find).sort(sort_by, pymongo.DESCENDING if descending else pymongo.ASCENDING)
        for document in all_documents:
            yield self._entity_type.parse_obj(document)

    def save(self, new_item: unit_of_work.T) -> None:
        self._assert_not_readonly(item=new_item)
        existing = self.collection.find_one({"_id": new_item.id.key()}, projection=["_id"])
        if existing:
            expected_version = new_item.version
            new_item.version = expected_version + 1
            result = self.collection.update_one(
                filter={"_id": new_item.id.key(), "version": expected_version},
                update={"$set": self._parse_to_mongo_document(item=new_item)},
            )
            if result.matched_count == 0:
                raise base_types.OptimisticLockError(
                    f"Entity [{new_item.id.key()}] was modified by another process"
                )
        else:
            self.collection.insert_one(self._parse_to_mongo_document(item=new_item))

    def find_by_id(
        self, entity_id: unit_of_work.U
    ) -> unit_of_work.T | None:
        cursor = self.collection.find({"_id": entity_id.key()})
        document = next(cursor, None)
        return self._entity_type.parse_obj(document) if document else None  # type: ignore

    def get_all(
            self,
            descending: bool = True,
            limit: int = 20,
            sort_by: str = "created_at"
    ) -> Iterator[unit_of_work.T]:
        all_documents = self.collection.find().sort(sort_by, pymongo.DESCENDING if descending else pymongo.ASCENDING).limit(limit=limit)
        for document in all_documents:
            yield self._entity_type.parse_obj(document)

    def _get_collection(self) -> pymongo.collection.Collection:
        return self.db[self._entity_type.__name__]

    @staticmethod
    def _parse_to_mongo_document(item: unit_of_work.T) -> dict[str, Any]:
        new_item: dict[str, Any] = json.loads(item.json())
        new_item.update({"_id": item.id.key()})
        return new_item
