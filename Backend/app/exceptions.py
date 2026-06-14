from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class NotFoundError(HTTPException):
    def __init__(self, entity: str, id: str = ""):
        msg = f"{entity} topilmadi"
        if id:
            msg += f" (id: {id})"
        super().__init__(status_code=404, detail=msg)


class ConflictError(HTTPException):
    def __init__(self, msg: str):
        super().__init__(status_code=409, detail=msg)


class ForbiddenError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Ruxsat yo'q")


class UnauthorizedError(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token yaroqsiz yoki muddati o'tgan")


class FileTooLargeError(HTTPException):
    def __init__(self, max_mb: int):
        super().__init__(status_code=413, detail=f"Fayl {max_mb}MB dan oshmasin")


class InvalidFileTypeError(HTTPException):
    def __init__(self):
        super().__init__(status_code=415, detail="Faqat jpg, jpeg, png, webp ruxsat etilgan")


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )
