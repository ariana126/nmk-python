from ddd import DomainEvent
from sqlalchemy.sql.schema import Identity


class UserRegistered(DomainEvent):
    def __init__(self, user_id: Identity):
        self.user_id = user_id