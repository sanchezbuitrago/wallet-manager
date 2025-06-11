from app.commons import logs
from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands, aggregates, exceptions, dtos
from app.auth.repository import user as  user_repository
from app.auth.domain.services import auth

_LOGGER = logs.get_logger()


def create_user(uow: unit_of_work.UnitOfWork, cmd: commands.CreateUserRequest) -> None:
    _LOGGER.info("Try to create a new user with email [%s]", cmd.email)
    repo: user_repository.FakeUserRepository = uow.get_custom_repository(entity_type=aggregates.User, repository_type=user_repository.FakeUserRepository)
    user = repo.find_by_email(email=cmd.email)
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
        repo.put(entity=new_user)
        _LOGGER.info("User with email [%s] created", cmd.email)