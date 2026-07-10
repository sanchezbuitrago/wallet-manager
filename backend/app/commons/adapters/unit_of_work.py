import abc
from typing import Generic, Iterator, TypeVar

from app.commons import base_types

T = TypeVar("T", bound=base_types.DomainEntity)
U = TypeVar("U", bound=base_types.EntityId)


class AbstractRepository(abc.ABC, Generic[T]):
    @abc.abstractmethod
    def __init__(self, uow: "AbstractUnitOfWork") -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_model_type(self) -> type[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def save(self, new_item: T) -> None:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_all(self, descending: bool, limit: int, sort_by: str) -> Iterator[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by_id(self, entity_id: U, entity_type: type[T]) -> T | None:
        raise NotImplementedError()

    @abc.abstractmethod
    def query(self) -> Iterator[T]:
        raise NotImplementedError()

    @abc.abstractmethod
    def find_by(self, find: dict[str, str], sort_by: str = "created_at", descending: bool = True) -> Iterator[T]:
        raise NotImplementedError()


class AbstractUnitOfWork(abc.ABC):
    @abc.abstractmethod
    def get_repo(self, entity_type: type[T]) -> AbstractRepository[T]:
        raise NotImplementedError()
