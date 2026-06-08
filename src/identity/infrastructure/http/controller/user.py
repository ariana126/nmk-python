from ddd import Identity
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel
from pydm import ServiceContainer

from framework.domain import Email, InvalidEmail
from framework.infrastructure.cqrs import CommandBus, QueryBus
from identity.application.command import RegisterUserCommand
from identity.application.query.get_user_by_id import GetUserByIdQuery
from identity.infrastructure.http import get_current_user_id

users_router = APIRouter(tags=["Users"], prefix="/users")
command_bus = ServiceContainer.get_instance().get_service(CommandBus)
query_bus = ServiceContainer.get_instance().get_service(QueryBus)


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "firstName": "Alice",
                "lastName": "Smith",
                "email": "alice@example.com",
                "password": "s3cr3t",
            }
        },
    )
    first_name: str
    last_name: str
    email: str
    password: str = Field(min_length=6)

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        try:
            Email.from_string(v)
        except InvalidEmail:
            raise ValueError(f"Invalid email address: '{v}'")
        return v


@users_router.post(
    "/",
    status_code=201,
    summary="Register a new user",
    responses={
        409: {
            "description": "A user with the given email is already registered.",
            "content": {
                "application/problem+json": {
                    "example": {
                        "type": "https://my-api-doc.dev/problems/user-already-exists",
                        "title": "User Already Exists",
                        "status": 409,
                        "detail": "User with email alice@example.com already exists.",
                        "email": "alice@example.com",
                    }
                }
            },
        },
        422: {
            "description": "Request body failed validation, or the email address is malformed.",
            "content": {
                "application/problem+json": {
                    "examples": {
                        "body-validation": {
                            "summary": "Body validation failed",
                            "value": {
                                "type": "https://my-api-doc.dev/problems/validation-error",
                                "title": "Validation Error",
                                "status": 422,
                                "errors": [
                                    {
                                        "field": "body.password",
                                        "msg": "String should have at least 6 characters",
                                    }
                                ],
                            },
                        },
                        "invalid-email": {
                            "summary": "Invalid email address",
                            "value": {
                                "type": "https://my-api-doc.dev/problems/invalid-email",
                                "title": "Invalid email address",
                                "status": 422,
                                "detail": "not-an-email is not a valid email address.",
                                "email": "not-an-email",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register_user(body: RegisterUserRequest) -> Response:
    await command_bus.execute(
        RegisterUserCommand(
            body.first_name,
            body.last_name,
            Email.from_string(body.email),
            body.password,
        )
    )

    return Response(status_code=201)


class UserResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "9b1d2e3a-4f5b-4c6d-8e7f-0a1b2c3d4e5f",
                "firstName": "Alice",
                "lastName": "Smith",
                "email": "alice@example.com",
            }
        },
    )
    id: str
    first_name: str
    last_name: str
    email: str


@users_router.get(
    "/me",
    summary="Get the authenticated user",
    responses={
        401: {
            "description": "The access token is missing, invalid, or expired.",
            "content": {
                "application/problem+json": {
                    "example": {
                        "type": "https://my-api-doc.dev/problems/unauthorized",
                        "title": "Unauthorized",
                        "status": 401,
                        "detail": "The access token is invalid or has expired.",
                    }
                }
            },
        },
    },
)
async def get_user(user_id: Identity = Depends(get_current_user_id)) -> UserResponse:
    user = await query_bus.execute(GetUserByIdQuery(user_id))
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
    )
