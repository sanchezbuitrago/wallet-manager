import abc
from typing import TypeVar, Generic, Dict, Type, List
from app.commons import base_types

T = TypeVar("T", bound=base_types.Aggregate)
U = TypeVar("U", bound=base_types.EntityId)


_IN_MEMORY_DB: Dict[Type[T], Dict[U, T]] = {}


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

    @abc.abstractmethod
    def get_by_field(self, field: str, value: str) -> T:
        ...


class UnitOfWork(SingletonBase):

    @abc.abstractmethod
    def get_default_repo(self, entity_type: Type[T]) -> BaseRepository[T]:
        ...


class FakeRepository(BaseRepository[T]):

    def __init__(self, entity_type: Type[T]):
        self.entity_type: Type[T] = entity_type

    def get_by_id(self, entity_id: U) -> T | None:
        if _IN_MEMORY_DB.get(self.entity_type):
            return _IN_MEMORY_DB[self.entity_type].get(entity_id)
        return None

    def put(self, entity: T) -> None:
        if not _IN_MEMORY_DB.get(self.entity_type):
            _IN_MEMORY_DB.update({self.entity_type: {entity.id: entity}})
        else:
            _IN_MEMORY_DB[self.entity_type].update({entity.id: entity})

    def get_by_field(self, field: str, value: str) -> T | None:
        print(_IN_MEMORY_DB)
        if _IN_MEMORY_DB.get(self.entity_type):
            for _, item in _IN_MEMORY_DB[self.entity_type].items():
                if item.model_dump().get(field) == value:
                    return item
        return None


class FakeUnitOfWork(UnitOfWork):

    _initialized = False

    def __init__(self) -> None:
        if self._initialized:
            return
        self._db: Dict[Type[T], Dict[U, T]] = {}
        self._repos: Dict[Type[T], FakeRepository[T]] = {}
        self._initialized = True

    def get_default_repo(self, entity_type: Type[T]) -> BaseRepository[T]:
        if self._repos and self._repos.get(entity_type):
            return self._repos.get(entity_type)
        else:
            new_repo = FakeRepository[entity_type](entity_type=entity_type)
            self._repos.update({entity_type: new_repo})
            return new_repo
