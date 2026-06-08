from dataclasses import dataclass

from ddd import Identity
from mediatr import Mediator

from identity.domain import UserRepository, User


@dataclass(frozen=True)
class GetUserByIdQuery:
    user_id: Identity


@Mediator.handler
class GetUserByIdQueryHandler:
    def __init__(self, user_repository: UserRepository):
        self.__user_repository = user_repository

    async def handle(self, query: GetUserByIdQuery) -> User:
        # TODO: Directly query the database for getting UserReadModel data, and don't expose the user aggregate root internal data.
        return self.__user_repository.get(query.user_id)
