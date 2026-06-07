from http import HTTPStatus

from ddd.domain.service import EntityNotFound
from starlette.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError

from framework.domain import InvalidEmail
from framework.infrastructure.http import ExceptionMapper, ProblemDetail


class FrameworkExceptionMapper(ExceptionMapper):
    @staticmethod
    def can_map(exception: Exception) -> bool:
        return isinstance(
            exception,
            (EntityNotFound, InvalidEmail, HTTPException, RequestValidationError),
        )

    @staticmethod
    def to_problem_detail(exception: Exception) -> ProblemDetail:
        match exception:
            case InvalidEmail():
                return ProblemDetail(
                    "invalid-email",
                    "Invalid email address",
                    400,
                    str(exception),
                    None,
                    {
                        "email": exception.email_address,
                    },
                )
            case EntityNotFound():
                return ProblemDetail(
                    "entity-not-found", "Entity not found", 404, str(exception)
                )
            case HTTPException():
                try:
                    http_status = HTTPStatus(exception.status_code)
                    title = http_status.phrase
                    type_slug = title.lower().replace(" ", "-")
                except ValueError:
                    title = "HTTP Error"
                    type_slug = f"http-{exception.status_code}"
                detail = str(exception.detail) if exception.detail else None
                return ProblemDetail(type_slug, title, exception.status_code, detail)
            case RequestValidationError():
                errors = [
                    {"field": ".".join(str(p) for p in e["loc"][1:]), "msg": e["msg"]}
                    for e in exception.errors()
                ]
                return ProblemDetail(
                    "validation-error",
                    "Validation Error",
                    400,
                    extension_members={"errors": errors},
                )
            case _:
                raise RuntimeError(f"Unexpected exception: {exception}")
