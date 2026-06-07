_TYPE_BASE_URL: str = "https://my-api-doc.dev/problems"
_BLANK_TYPE: str = "about:blank"


class ProblemDetail:
    def __init__(
        self,
        type_uri: str,
        title: str,
        status: int,
        detail: str | None = None,
        instance: str | None = None,
        extension_members: dict[str, object] | None = None,
    ) -> None:
        self.__type_uri = type_uri
        self.__title = title
        # TODO: Check status is a valid http status code
        self.__status = status
        self.__detail = detail
        self.__instance = instance
        self.__extension_members = extension_members

    @classmethod
    def for_unknown_error(cls) -> "ProblemDetail":
        return cls(_BLANK_TYPE, "Internal Server Error", 500)

    @property
    def status(self) -> int:
        return self.__status

    @property
    def as_response_body(self) -> dict[str, object]:
        body: dict[str, object] = {
            "type": f"{_TYPE_BASE_URL}/{self.__type_uri}"
            if _BLANK_TYPE != self.__type_uri
            else _BLANK_TYPE,
            "title": self.__title,
            "status": self.__status,
        }
        if self.__detail is not None:
            body["detail"] = self.__detail
        if self.__instance is not None:
            body["instance"] = self.__instance
        if self.__extension_members is not None:
            body.update(self.__extension_members)
        return body
