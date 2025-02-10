class BackendError(RuntimeError):
    _message: str

    def __init__(self, message: str = "") -> None:
        self._message = message

    def __str__(self):
        return self._message


class ServiceError(BackendError):
    pass


class InvalidTokenError(ServiceError):
    pass


class AuthenticationError(ServiceError):
    pass


class AuthorizationError(ServiceError):
    pass
