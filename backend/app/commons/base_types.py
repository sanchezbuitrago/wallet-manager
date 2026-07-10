import pydantic


class ValueObject(pydantic.BaseModel):
    class Config:
        frozen = True


class EntityId(pydantic.BaseModel):
    value: str = pydantic.Field(default=None, init=False)

    @pydantic.model_validator(mode='before')
    def build_value(cls, values):
        parts = [str(values[k]) for k in values if k != 'value']
        values['value'] = '#'.join(parts)
        return values

    def key(self) -> str:
        return self.value

    class Config:
        frozen = True
        arbitrary_types_allowed = False

class DomainEntity(pydantic.BaseModel):
    id: EntityId


class Aggregate(DomainEntity):
    pass


class ForeignAggregate(DomainEntity):
    """Base class for entities that reference an aggregate owned by another context.
    Semantically identical to Aggregate, but signals that this entity's lifecycle
    is managed elsewhere."""
    pass


class PhoneNumber(pydantic.BaseModel):
    country_code: str
    number: str