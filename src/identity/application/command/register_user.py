from dataclasses import dataclass

from mediatr import Mediator
from ddd import Clock
from ddd.application import Command

from framework.domain import Email
from identity.domain import UserRepository, User


class UserAlreadyExists(RuntimeError):
    def __init__(self, message: str, email: Email) -> None:
        super().__init__(message)
        self.email = email

    @staticmethod
    def with_email(email: Email) -> "UserAlreadyExists":
        return UserAlreadyExists(f"User {email.as_string} already exists.", email)


@dataclass
class RegisterUserCommand(Command):
    first_name: str
    last_name: str
    email: Email
    password: str


@Mediator.handler
class RegisterUserCommandHandler:
    def __init__(self, user_repository: UserRepository, clock: Clock):
        self.__user_repository = user_repository
        self.__clock = clock

    async def handle(self, cmd: RegisterUserCommand) -> None:
        self.__validate_user_is_not_exists(cmd.email)
        new_user = User.register(
            cmd.first_name, cmd.last_name, cmd.email, cmd.password, self.__clock.now()
        )
        self.__user_repository.save(new_user)

    def __validate_user_is_not_exists(self, email: Email) -> None:
        user: User | None = self.__user_repository.find_by_email(email)
        if user is not None:
            raise UserAlreadyExists.with_email(email)
