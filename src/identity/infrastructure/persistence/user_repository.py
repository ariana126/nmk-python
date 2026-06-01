from sqlalchemy import select
from ddd.domain.service.repository import AggregateRootType

from framework.domain.value.email import Email
from framework.infrastructure import SQLAlchemyBaseRepository
from identity.domain import UserRepository, User
from identity.infrastructure.persistence.tables import users_table


class SQLAlchemyUserRepository(UserRepository, SQLAlchemyBaseRepository):
    @property
    def entity(self) -> type[AggregateRootType]:
        return User

    def find_by_email(self, email: Email) -> User | None:
        return self.connection.get_session().execute(
            select(User).where(users_table.c.email == email)
        ).scalar_one_or_none()