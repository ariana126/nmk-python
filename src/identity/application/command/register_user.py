from dataclasses import dataclass

from mediatr import Mediator
from ddd import Clock
from ddd.application import Command

from framework.domain import Email
from identity.domain import UserRepository, User


class UserAlreadyExists(RuntimeError):
    @staticmethod
    def with_email(email: Email) -> "UserAlreadyExists":
        return UserAlreadyExists(f"User {email.as_string} already exists.")


@dataclass(frozen=True)
class RegisterUserCommand(Command):
    email: Email
    password: str


@Mediator.handler
class RegisterUserCommandHandler:
    def __init__(self, user_repository: UserRepository, clock: Clock):
        self.__user_repository = user_repository
        self.__clock = clock

    async def handle(self, cmd: RegisterUserCommand) -> None:
        self.__validate_user_is_not_exists(cmd.email)
        new_user = User.register(cmd.email, cmd.password, self.__clock.now())
        self.__user_repository.save(new_user)

    def __validate_user_is_not_exists(self, email: Email) -> bool:
        user: User|None = self.__user_repository.find_by_email(email)
        if not user is None:
            raise UserAlreadyExists.with_email(email)