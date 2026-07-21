import random
import string
import time

from app.commons import logs
from app.commons import domain_events
from app.commons.adapters import unit_of_work
from app.auth.domain.model import commands
from app.auth.domain.model import exceptions
from app.auth.domain.model import aggregates

_LOGGER = logs.get_logger()

_VERIFICATION_CODE_LENGTH = 6


def _generate_verification_code() -> str:
    """Generate a 6-digit numeric verification code."""
    return "".join(random.choices(string.digits, k=_VERIFICATION_CODE_LENGTH))


def _check_phone_uniqueness(
        full_phone: str,
        exclude_user_id: str | None,
        repo,
) -> None:
    """Validate that the phone number is not used by another active user.

    Args:
        full_phone: The full phone number to check.
        exclude_user_id: User ID to exclude from the check (for updates).
        repo: The user repository.

    Raises:
        PhoneNumberAlreadyExistError: If another user already has this phone.
    """
    phone_user = next(repo.find_by(find={"full_phone": full_phone}), None)
    if phone_user and phone_user.id.value != exclude_user_id:
        raise exceptions.PhoneNumberAlreadyExistError()


def create_user(
        cmd: commands.CreateUserRequest,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Register a new user in pending status and request a verification code.

    If a user with the same email already exists and is pending, update their
    data and resend the verification code. Validates that the phone number
    is not already used by another user.

    Args:
        cmd: The user creation request.
        uow: Unit of work for data access.

    Raises:
        UserAlreadyExistError: If a user with the same email is already active.
        PhoneNumberAlreadyExistError: If the phone is used by another user.
    """
    _LOGGER.info("Try to create a new user with email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User)
    full_phone = f"{cmd.phone_number.country_code}{cmd.phone_number.number}"
    existing_user = next(repo.find_by(find={"email": cmd.email}), None)

    if existing_user and existing_user.is_active:
        _LOGGER.info("Active user with email [%s] already exist", cmd.email)
        raise exceptions.UserAlreadyExistError()

    if existing_user:
        _LOGGER.info("Updating pending user with email [%s]", cmd.email)
        _check_phone_uniqueness(full_phone, existing_user.id.value, repo)
        existing_user.first_names = cmd.first_names
        existing_user.last_names = cmd.last_names
        existing_user.phone_number = cmd.phone_number
        existing_user.full_phone = full_phone
        existing_user.pin = cmd.pin
        code = _generate_verification_code()
        existing_user.assign_verification_code(code)
        repo.save(new_item=existing_user)
        uow.add_event(domain_events.TokenRequested(
            user_id=existing_user.id.value,
            phone_number=existing_user.full_phone,
            verification_code=code,
        ))
        _LOGGER.info("Verification code sent for existing user [%s]", cmd.email)
        return

    _check_phone_uniqueness(full_phone, None, repo)

    new_user = aggregates.User.create(
        first_names=cmd.first_names,
        last_names=cmd.last_names,
        pin=cmd.pin,
        phone_number=cmd.phone_number,
        email=cmd.email,
    )
    code = _generate_verification_code()
    new_user.assign_verification_code(code)
    repo.save(new_item=new_user)
    uow.add_event(domain_events.TokenRequested(
        user_id=new_user.id.value,
        phone_number=new_user.full_phone,
        verification_code=code,
    ))
    _LOGGER.info("User with email [%s] created in PENDING status", cmd.email)


def verify_token(
        cmd: commands.VerifyTokenRequest,
        uow: unit_of_work.AbstractUnitOfWork,
) -> None:
    """Verify the user's verification code and activate their account.

    Args:
        cmd: The verification request with email and code.
        uow: Unit of work for data access.

    Raises:
        EmailNotFoundError: If no user is found with the given email.
        InvalidVerificationCodeError: If the code is incorrect.
        VerificationCodeExpiredError: If the code has expired.
    """
    _LOGGER.info("Try to verify token for email [%s]", cmd.email)
    repo = uow.get_repo(entity_type=aggregates.User)
    user = next(repo.find_by(find={"email": cmd.email}), None)

    if not user:
        _LOGGER.info("No user found with email [%s] for verification", cmd.email)
        raise exceptions.EmailNotFoundError()

    if not user.is_verification_code_valid(cmd.code):
        if user.verification_code is not None and user.verification_code_expires_at is not None:
            if time.time() >= user.verification_code_expires_at:
                _LOGGER.info("Verification code expired for email [%s]", cmd.email)
                raise exceptions.VerificationCodeExpiredError()
        _LOGGER.info("Invalid verification code for email [%s]", cmd.email)
        raise exceptions.InvalidVerificationCodeError()

    user.activate()
    repo.save(new_item=user)
    uow.add_event(domain_events.TokenVerified(
        user_id=user.id.value,
        phone_number=user.full_phone,
    ))
    uow.add_event(domain_events.UserCreated(
        user_id=user.id.value,
    ))
    _LOGGER.info("User with email [%s] verified and activated", cmd.email)


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
