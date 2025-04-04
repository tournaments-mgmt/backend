from starlette import status
from starlette.responses import JSONResponse

from tournaments_backend.errors.backend import BackendError
from tournaments_backend.errors.services import (
    AuthenticationError,
    InvalidTokenError,
    AuthorizationError,
)


def register(app):
    @app.exception_handler(BackendError)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )

    @app.exception_handler(AuthenticationError)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={},
        )

    @app.exception_handler(InvalidTokenError)
    @app.exception_handler(AuthorizationError)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={},
        )
