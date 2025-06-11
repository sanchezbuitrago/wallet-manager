from typing import Dict, Type
from app.commons.adapters import unit_of_work
from app.auth.domain.model import aggregates


class FakeUserRepository(unit_of_work.FakeRepository[aggregates.User]):

    def __init__(self, db: Dict[Type[unit_of_work.T], Dict[unit_of_work.U, unit_of_work.T]], entity_type: Type[unit_of_work.T]):
        super().__init__(db, entity_type)

    def find_by_email(self, email: str) -> unit_of_work.T | None:
        users = self.db.get(aggregates.User, {})
        for _, user in users.items():
            if user.email == email:
                return user
        return None


