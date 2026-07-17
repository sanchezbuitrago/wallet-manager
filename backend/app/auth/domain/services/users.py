from app.commons import logs
from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands
from app.auth.domain.model import exceptions
from app.auth.domain.model import aggregates

_LOGGER = logs.get_logger()


def create_user(
        cmd: commands.CreateUserRequest,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Register a new user.

    Args:
        cmd: The user creation request.
        uow: Unit of work for data access.

    Raises:
        UserAlreadyExistError: If a user with the same email exists.
    """
    _LOGGER.info("Try to create a new user with email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"email": cmd.email}), None)
    if user:
        _LOGGER.info("User with email [%s] already exist with id [%s]", cmd.email, user.id.value)
        raise exceptions.UserAlreadyExistError()

    new_user = aggregates.User.create(
        first_names=cmd.first_names,
        last_names=cmd.last_names,
        pin=cmd.pin,
        phone_number=cmd.phone_number,
        email=cmd.email
    )
    repo.save(new_item=new_user)
    _LOGGER.info("User with email [%s] created", cmd.email)


def find_user_by_phone(
        phone_number: str,
        uow: unit_of_work.AbstractUnitOfWork,
) -> aggregates.User | None:
    """Find a user by their phone number.

    Args:
        phone_number: The full phone number to search for.
        uow: Unit of work for data access.

    Returns:
        The matching User, or None if not found.
    """
    _LOGGER.info("Looking for user with phone [%s]", phone_number)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"full_phone": phone_number}), None)
    if user:
        _LOGGER.info("User found: [%s]", user.id.value)
    else:
        _LOGGER.info("No user found with phone [%s]", phone_number)
    return user


def change_pin(
    uow: unit_of_work.AbstractUnitOfWork,
    cmd: commands.ChangePinRequest,
) -> None:
    """Change a user's PIN.

    Args:
        uow: Unit of work for data access.
        cmd: The change-PIN request with old and new PIN values.
    """
    _LOGGER.info("Try to change pin")
