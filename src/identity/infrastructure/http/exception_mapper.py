from framework.infrastructure.http import ExceptionMapper, ProblemDetail
from identity.application.command import UserAlreadyExists, InvalidCredentials


class IdentityExceptionMapper(ExceptionMapper):
    @staticmethod
    def can_map(exception: Exception) -> bool:
        return isinstance(exception, (UserAlreadyExists, InvalidCredentials))

    @staticmethod
    def to_problem_detail(exception: Exception) -> ProblemDetail:
        match exception:
            case UserAlreadyExists():
                return ProblemDetail(
                    "user-already-exists",
                    "User Already Exists",
                    409,
                    str(exception),
                    None,
                    {
                        "email": exception.email.as_string,
                    },
                )
            case InvalidCredentials():
                return ProblemDetail(
                    "invalid-credentials",
                    "Invalid Credentials",
                    401,
                    str(exception),
                )
            case _:
                raise RuntimeError(f"Unexpected exception: {exception}")
