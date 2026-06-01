from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from ddd import Identity
from framework.domain import Email


class IdentityType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.as_string if value is not None else None

    def process_result_value(self, value, dialect):
        return Identity.from_string(value) if value is not None else None


class EmailType(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return value.as_string if value is not None else None

    def process_result_value(self, value, dialect):
        return Email.from_string(value) if value is not None else None
