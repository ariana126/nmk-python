from ddd import Identity
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydm import ServiceContainer

from framework.application import TokenService

_bearer_scheme = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> Identity:
    token_service = ServiceContainer.get_instance().get_service(TokenService)
    user_id = token_service.verify(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=401, detail="The access token is invalid or has expired."
        )
    return user_id


async def require_authentication(
    _: Identity = Depends(get_current_user_id),
) -> None:
    pass
