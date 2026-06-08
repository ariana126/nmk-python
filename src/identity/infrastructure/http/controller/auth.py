from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from pydm import ServiceContainer

from framework.domain import Email
from framework.infrastructure.cqrs import CommandBus
from identity.application.command import LoginCommand

auth_router = APIRouter(tags=["Auth"])
command_bus = ServiceContainer.get_instance().get_service(CommandBus)


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"email": "alice@example.com", "password": "s3cr3t"}
        }
    )
    email: str
    password: str


@auth_router.post(
    "/login",
    summary="Authenticate a user",
    responses={
        200: {
            "description": "Authentication successful.",
            "content": {
                "application/json": {
                    "example": {
                        "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    }
                }
            },
        },
        401: {
            "description": "The email or password is incorrect.",
            "content": {
                "application/problem+json": {
                    "example": {
                        "type": "https://my-api-doc.dev/problems/invalid-credentials",
                        "title": "Invalid Credentials",
                        "status": 401,
                        "detail": "Invalid email or password provided.",
                    }
                }
            },
        },
        400: {
            "description": "The email address is malformed.",
            "content": {
                "application/problem+json": {
                    "example": {
                        "type": "https://my-api-doc.dev/problems/invalid-email",
                        "title": "Invalid email address",
                        "status": 400,
                        "detail": "Invalid email address: 'not-an-email'",
                        "email": "not-an-email",
                    }
                }
            },
        },
    },
)
async def login(body: LoginRequest) -> JSONResponse:
    token: str = await command_bus.execute(
        LoginCommand(Email.from_string(body.email), body.password)
    )
    return JSONResponse({"accessToken": token})
