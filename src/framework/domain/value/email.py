import re

from ddd import ValueObject

from framework.domain import DomainException

class InvalidEmail(DomainException):
    def __init__(self, message: str):
        super().__init__(message)

    @staticmethod
    def provided(email_address: str) -> 'InvalidEmail':
        return InvalidEmail(f"Invalid email address: {email_address!r}")


class Email(ValueObject):
    __EMAIL_PATTERN = re.compile(
        r"^(?=.{3,254}$)(?=.{1,64}@)"
        r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+"
        r"(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
        r"@"
        r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
        r"[a-z0-9]{2,63}$",
        re.IGNORECASE,
    )

    def __init__(self, value: str):
        normalized = value.strip().lower()
        if not self.__EMAIL_PATTERN.match(normalized):
            raise InvalidEmail.provided(normalized)
        self.__value = normalized

    @classmethod
    def from_string(cls, email: str) -> 'Email':
        return Email(email)

    @property
    def as_string(self) -> str:
        return self.__value

    def __str__(self):
        return self.__value