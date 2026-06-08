from datetime import datetime, timedelta, timezone

import jwt

from identity.application.service.token_service import TokenService


class JwtTokenService(TokenService):
    _ALGORITHM = "HS256"

    def __init__(self, secret: str) -> None:
        self.__secret = secret

    def issue_for_user(self, user_id: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(hours=24),
        }
        return jwt.encode(payload, self.__secret, algorithm=self._ALGORITHM)
