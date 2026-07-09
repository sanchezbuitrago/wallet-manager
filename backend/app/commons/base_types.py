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

    class Config:
        frozen = True
        arbitrary_types_allowed = False

class Aggregate(pydantic.BaseModel):
    id: EntityId


class PhoneNumber(pydantic.BaseModel):
    country_code: str
    number: str