from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi.responses import JSONResponse

from framework.infrastructure.http import ExceptionMapper, ProblemDetail
from framework.infrastructure.http import FrameworkExceptionMapper
from identity.infrastructure.http import IdentityExceptionMapper

_EXCEPTION_MAPPERS: tuple[type(ExceptionMapper), ...] = (
    FrameworkExceptionMapper,
    IdentityExceptionMapper,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        return __get_error_response(exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return __get_error_response(exc)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return __get_error_response(exc)


def __get_error_response(exception: Exception) -> JSONResponse:
    problem_detail = __get_problem_detail(exception)
    return JSONResponse(
        headers={"Content-Type": "application/problem+json"},
        status_code=problem_detail.status,
        content=problem_detail.as_response_body,
    )


def __get_problem_detail(exception: Exception) -> ProblemDetail:
    for mapper in _EXCEPTION_MAPPERS:
        if not mapper.can_map(exception):
            continue
        return mapper.to_problem_detail(exception)
    return ProblemDetail.for_unknown_error()
