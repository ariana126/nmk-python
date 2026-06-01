from fastapi import APIRouter, Response
from mediatr import Mediator
from pydantic import BaseModel, ConfigDict
from pydm import ServiceContainer

from framework.domain import Email, InvalidEmail
from framework.infrastructure.cqrs import CommandBus
from identity.application.command import RegisterUserCommand, UserAlreadyExists

users_router = APIRouter(tags=["Users"])
command_bus = ServiceContainer.get_instance().get_service(CommandBus)


class RegisterUserRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {"email": "alice@example.com", "password": "s3cr3t"}
    })
    email: str
    password: str


@users_router.post(
    "/users",
    status_code=201,
    responses={
        409: {"description": "User already exists"},
        422: {"description": "Invalid email format"},
    },
)
async def register_user(body: RegisterUserRequest) -> Response:
    try:
        email = Email.from_string(body.email)
    except InvalidEmail as e:
        return Response(content=str(e), status_code=422)

    try:
        await command_bus.execute(RegisterUserCommand(email=email, password=body.password))
    except UserAlreadyExists as e:
        return Response(content=str(e), status_code=409)

    return Response(status_code=201)