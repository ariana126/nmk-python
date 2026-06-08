from ddd import DomainEvent, Identity


class UserRegistered(DomainEvent):
    def __init__(self, user_id: Identity):
        self.user_id = user_id

    def __repr__(self):
        return f"UserRegistered(user_id={self.user_id.as_string})"
