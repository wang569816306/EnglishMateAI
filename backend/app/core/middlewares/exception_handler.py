from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from app.core.exceptions import APIException
from app.schemas.response import ApiResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    处理HTTP异常（404, 405等）
    """
    return JSONResponse(
        content=ApiResponse(
            code=exc.status_code,
            msg=exc.detail,
            data=None
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    处理参数验证错误
    """
    return JSONResponse(
        content=ApiResponse(
            code=422,
            msg="参数验证失败",
            data={"errors": exc.errors()}
        ).model_dump()
    )


async def global_exception_handler(request: Request, exc: Exception):
    """
    处理所有其他异常
    """
    # 1. 自定义业务异常
    if isinstance(exc, APIException):
        return JSONResponse(
            content=ApiResponse(
                code=exc.code,
                msg=exc.msg,
                data=None
            ).model_dump()
        )

    # 2. 服务器异常
    else:
        return JSONResponse(
            content=ApiResponse(
                code=500,
                msg=f"服务器内部错误: {str(exc)}",
                data=None
            ).model_dump()
        )