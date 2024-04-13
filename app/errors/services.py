from starlette import status
from starlette.exceptions import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)


class AlreadyManagedError(HTTPException):
    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail, headers)


class AlreadyConnectedError(HTTPException):
    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, detail, headers)


class CannotProceedError(HTTPException):
    def __init__(self, detail: str | None = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status.HTTP_406_NOT_ACCEPTABLE, detail, headers)
