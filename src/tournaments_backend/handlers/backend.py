from starlette import status
from starlette.responses import JSONResponse

from tournaments_backend.errors.backend import BackendException


def register(app):
    @app.exception_handler(BackendException)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )
