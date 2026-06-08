from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from ddd import AggregateRoot, Identity

from framework.domain import Email
from identity.domain.event.user_registered import UserRegistered

if TYPE_CHECKING:
    from identity.domain.service.password_hasher import PasswordHasher


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

    @property
    def first_name(self) -> str:
        return self.__first_name

    @property
    def last_name(self) -> str:
        return self.__last_name

    @property
    def email(self) -> Email:
        return self.__email

    @staticmethod
    def register(
        first_name: str, last_name: str, email: Email, password: str, date: datetime
    ) -> "User":
        user = User(Identity.new(), first_name, last_name, email, password, date)
        user._record_that(UserRegistered(user.id))
        return user

    def verify_password(self, plain: str, hasher: PasswordHasher) -> bool:
        return hasher.verify(plain, self.__password)
