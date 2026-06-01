from fastapi import APIRouter, Response
from mediatr import Mediator
from pydantic import BaseModel
from pydm import ServiceContainer

from framework.domain import Email, InvalidEmail
from framework.infrastructure.cqrs import CommandBus
from identity.application.command import RegisterUserCommand, UserAlreadyExists

users_router = APIRouter()
command_bus = ServiceContainer.get_instance().get_service(CommandBus)


class RegisterUserRequest(BaseModel):
    email: str
    password: str


@users_router.post("/users", status_code=201)
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