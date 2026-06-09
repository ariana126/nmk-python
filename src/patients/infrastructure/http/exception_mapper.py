from framework.infrastructure.http import ExceptionMapper, ProblemDetail
from patients.application.command.register_patient import PatientExists


class PatientsExceptionMapper(ExceptionMapper):
    @staticmethod
    def can_map(exception: Exception) -> bool:
        return isinstance(exception, PatientExists)

    @staticmethod
    def to_problem_detail(exception: Exception) -> ProblemDetail:
        match exception:
            case PatientExists():
                return ProblemDetail(
                    "patient-already-exists",
                    "Patient Already Exists",
                    409,
                    str(exception),
                )
            case _:
                raise RuntimeError(f"Unexpected exception: {exception}")
