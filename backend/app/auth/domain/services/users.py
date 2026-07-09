from app.commons import logs
from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands, exceptions
from app.commons.users.domain.models import aggregates

_LOGGER = logs.get_logger()


def create_user(
        cmd: commands.CreateUserRequest,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    _LOGGER.info("Try to create a new user with email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User, )
    user = repo.find_by(find={"email": cmd.email})
    if user:
        _LOGGER.info("User with email [%s] already exist with email [%s]", cmd.email, user.id.value)
        raise exceptions.UserAlreadyExistError()
    else:
        new_user = aggregates.User.create(
            first_names=cmd.first_names,
            last_names=cmd.last_names,
            pin=cmd.pin,
            phone_number=cmd.phone_number,
            email=cmd.email
        )
        repo.save(new_item=new_user)
        _LOGGER.info("User with email [%s] created", cmd.email)


def change_pin(uow: unit_of_work.AbstractUnitOfWork, cmd: commands.ChangePINRequest) -> None:
    _LOGGER.info("Try to change pin")
