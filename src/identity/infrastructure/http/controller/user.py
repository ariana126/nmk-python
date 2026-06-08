from fastapi import APIRouter, Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydm import ServiceContainer

from framework.domain import Email
from framework.infrastructure.cqrs import CommandBus
from identity.application.command import RegisterUserCommand

users_router = APIRouter(tags=["Users"])
command_bus = ServiceContainer.get_instance().get_service(CommandBus)


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


@users_router.post(
    "/users",
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
