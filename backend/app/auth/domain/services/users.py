from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands, aggregates, exceptions


def create_user(uow: unit_of_work.UnitOfWork, cmd: commands.CreateUserRequest) -> None:
    repo = uow.get_default_repo(entity_type=aggregates.User)
    user = repo.get_by_id(entity_id=aggregates.UserId(id="1234"))
    if user:
        raise exceptions.UserAlreadyExistError()
    else:
        new_user = aggregates.User.create(
            first_names=cmd.first_names,
            last_names=cmd.last_names,
            pin=cmd.pin,
            phone_number=cmd.phone_number,
            email=cmd.email
        )
        repo.put(entity=new_user)