from fastapi import FastAPI


def register(app: FastAPI):
    pass
    # @app.exception_handler(NotFoundError)
    # async def handler(request, exc):
    #     return JSONResponse(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         content={"message": str(exc)},
    #     )
    #
    # @app.exception_handler(AlreadyManagedError)
    # async def handler(request, exc):
    #     return JSONResponse(
    #         status_code=status.HTTP_409_CONFLICT,
    #         content={"message": str(exc)},
    #     )
    #
    # @app.exception_handler(CannotProceedError)
    # async def handler(request, exc):
    #     return JSONResponse(
    #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
    #         content={"message": str(exc)},
    #     )
