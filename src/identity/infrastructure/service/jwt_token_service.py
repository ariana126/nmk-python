from datetime import datetime, timedelta, timezone

import jwt
from ddd import Identity

from framework.application import TokenService


class JwtTokenService(TokenService):
    _ALGORITHM = "HS256"

    def __init__(self, secret: str) -> None:
        self.__secret = secret

    def issue_for_user(self, user_id: Identity) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id.as_string,
            "iat": now,
            "exp": now + timedelta(hours=24),
        }
        return jwt.encode(payload, self.__secret, algorithm=self._ALGORITHM)

    def verify(self, token: str) -> Identity | None:
        try:
            payload = jwt.decode(token, self.__secret, algorithms=[self._ALGORITHM])
        except jwt.InvalidTokenError:
            return None
        return Identity.from_string(payload["sub"])
