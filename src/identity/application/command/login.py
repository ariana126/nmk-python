from dataclasses import dataclass

from ddd.application import Command, CommandHandler
from mediatr import Mediator

from framework.domain import Email
from identity.application.service import TokenService
from identity.domain import UserRepository, PasswordHasher


class InvalidCredentials(RuntimeError):
    @staticmethod
    def provided() -> "InvalidCredentials":
        return InvalidCredentials("Invalid email or password provided.")


@dataclass
class LoginCommand(Command):
    email: Email
    password: str


@Mediator.handler
class LoginCommandHandler(CommandHandler):
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self.__user_repository = user_repository
        self.__password_hasher = password_hasher
        self.__token_service = token_service

    async def handle(self, command: LoginCommand) -> str:
        user = self.__user_repository.find_by_email(command.email)
        if user is None or not user.verify_password(
            command.password, self.__password_hasher
        ):
            raise InvalidCredentials.provided()
        return self.__token_service.issue_for_user(user.id)
