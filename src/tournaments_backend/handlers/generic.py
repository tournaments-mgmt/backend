import logging
import traceback

from starlette import status
from starlette.responses import JSONResponse

_logger = logging.getLogger(__name__)


def register(app):
    @app.exception_handler(NotImplementedError)
    async def handler(request, exc):
        _logger.error(f"{exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def handler(request, exc):
        _logger.error(f"{exc}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Invalid field"}
        )
