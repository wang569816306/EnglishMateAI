from fastapi import Request, Response
from fastapi.routing import APIRoute
from app.schemas.response import ApiResponse
from typing import Callable, Any
import json

class UniformResponse(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Any]:
        original_handler = super().get_route_handler()

        async def route_handler(request: Request) -> Response:
            # 执行原接口
            response = await original_handler(request)

            # 如果已经是 ApiResponse，不处理
            if isinstance(response, ApiResponse):
                return response

            # 如果是流式、文件，不处理
            if hasattr(response, "body_iterator") or hasattr(response, "stream"):
                return response

            # 检查是否是错误响应（通过状态码判断）
            if hasattr(response, 'status_code') and response.status_code >= 400:
                return response

            # 自动包装成统一格式
            return ApiResponse(code=200, msg="success", data=response)

        return route_handler