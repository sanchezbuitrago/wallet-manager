import decimal

import pydantic


class ValueObject(pydantic.BaseModel):
    """Base class for immutable value objects."""

    class Config:
        frozen = True


class EntityId(pydantic.BaseModel):
    """Base class for entity identifiers.

    Automatically builds a composite ``value`` from all fields
    except ``value`` itself, joined by ``#``.
    """

    value: str = pydantic.Field(default=None, init=False)

    @pydantic.model_validator(mode='before')
    def build_value(cls, values: dict) -> dict:
        """Compute the composite ID string from the model fields."""
        parts = [str(values[k]) for k in values if k != 'value']
        values['value'] = '#'.join(parts)
        return values

    def key(self) -> str:
        """Return the string key used for storage lookups."""
        return self.value

    class Config:
        frozen = True
        arbitrary_types_allowed = False


class DomainEntity(pydantic.BaseModel):
    """Base class for all domain entities."""

    id: EntityId


class OptimisticLockError(Exception):
    """Raised when a concurrent modification is detected on an entity."""
    pass


class Aggregate(DomainEntity):
    """Base class for aggregates that own their lifecycle."""

    version: int = 1


class ForeignAggregate(DomainEntity):
    """Base class for entities that reference an aggregate owned by another context.

    Semantically identical to Aggregate, but signals that this entity's lifecycle
    is managed elsewhere.
    """


class PhoneNumber(pydantic.BaseModel):
    """Phone number split into country code and local number."""

    country_code: str
    number: str


class Money(pydantic.BaseModel):
    """Monetary value with a currency code."""

    amount: decimal.Decimal
    currency: str = "COP"
