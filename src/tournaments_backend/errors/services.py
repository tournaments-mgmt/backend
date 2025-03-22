from tournaments_backend.errors.backend import BackendError


class ServiceError(BackendError):
    pass


class InvalidTokenError(ServiceError):
    pass


class AuthenticationError(ServiceError):
    pass


class AuthorizationError(ServiceError):
    pass


class NotFoundError(ServiceError):
    pass
