import abc
from typing import TypeVar, Generic, Dict, Type, List
from app.commons import base_types

T = TypeVar("T", bound=base_types.Aggregate)
U = TypeVar("U", bound=base_types.EntityId)


class SingletonBase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]


class BaseRepository(Generic[T]):
    @abc.abstractmethod
    def put(self, entity: T) -> None:
        ...

    @abc.abstractmethod
    def get_by_id(self, entity_id: U) -> T:
        ...


class UnitOfWork(SingletonBase):
    @abc.abstractmethod
    def get_default_repo(self, entity_type: Type[T]) -> BaseRepository[T]:
        ...


class FakeRepository(BaseRepository[T]):

    def __init__(self, db: Dict[Type[T], Dict[U, T]],
                 entity_type: Type[T]):
        self.db: Dict[Type[T], Dict[U, T]] = db
        self.entity_type: Type[T] = entity_type

    def get_by_id(self, entity_id: U) -> T | None:
        if self.db.get(self.entity_type):
            return self.db[self.entity_type].get(entity_id)
        return None

    def put(self, entity: T) -> None:
        print(self.db)
        if not self.db.get(self.entity_type):
            self.db.update({self.entity_type: {entity.id: entity}})
        else:
            self.db[self.entity_type].update({entity.id: entity})
        print(self.db)


class FakeUnitOfWork(UnitOfWork):
    _initialized = False

    def __init__(self):
        if self._initialized:
            return
        self._db: Dict[Type[T], Dict[U, T]] = {}
        self._repos: Dict[Type[T], FakeRepository[T]] = {}
        self._initialized = True

    def get_default_repo(self, entity_type: Type[T]) -> BaseRepository[T]:
        if self._repos and self._repos.get(entity_type):
            return self._repos.get(entity_type)
        else:
            new_repo = FakeRepository[entity_type](db=self._db, entity_type=entity_type)
            self._repos.update({entity_type: new_repo})
            return new_repo
