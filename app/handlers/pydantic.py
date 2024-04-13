import pydantic
from fastapi import FastAPI
from starlette import status
from starlette.responses import JSONResponse


def register(app: FastAPI):
    @app.exception_handler(pydantic.ValidationError)
    async def handler(request, exc):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": str(exc)},
        )
