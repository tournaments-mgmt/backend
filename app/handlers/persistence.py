from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse

from errors.persistence import ORMError, NotFoundError


def register(app: FastAPI):
    @app.exception_handler(ORMError)
    async def handler_orm_error(request, exc):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)}
        )

    @app.exception_handler(NotFoundError)
    async def handler_not_found_error(request, exc):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)}
        )
