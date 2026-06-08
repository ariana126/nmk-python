from datetime import datetime

from ddd import AggregateRoot, Identity

from framework.domain import Email
from identity.domain.event.user_registered import UserRegistered


class User(AggregateRoot):
    def __init__(
        self,
        _id: Identity,
        first_name: str,
        last_name: str,
        email: Email,
        password: str,
        registered_at: datetime,
    ) -> None:
        super().__init__(_id)
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__password = password
        self.__registered_at = registered_at

    @staticmethod
    def register(
        first_name: str, last_name: str, email: Email, password: str, date: datetime
    ) -> "User":
        user = User(Identity.new(), first_name, last_name, email, password, date)
        user._record_that(UserRegistered(user.id))
        return user
