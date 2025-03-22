from tournaments_backend.errors.services import ServiceError


class AlreadyManagedError(ServiceError):
    pass


class AlreadyConnectedError(ServiceError):
    pass


class CannotProceedError(ServiceError):
    pass
