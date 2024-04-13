from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from errors.api import UnauthorizedError


def register(app: FastAPI):
    @app.exception_handler(UnauthorizedError)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": str(exc)},
        )
