from dataclasses import dataclass

from ddd import Identity
from mediatr import Mediator

from identity.domain import UserRepository, User


@dataclass(frozen=True)
class UserReadModel:
    id: str
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class GetUserByIdQuery:
    user_id: Identity


@Mediator.handler
class GetUserByIdQueryHandler:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    async def handle(self, query: GetUserByIdQuery) -> UserReadModel:
        # TODO: Directly query the database for getting UserReadModel data
        user: User = self.__user_repository.get(query.user_id)
        return UserReadModel(
            user.id.as_string,
            user._User__email.as_string,
            user._User__first_name,
            user._User__last_name,
        )
