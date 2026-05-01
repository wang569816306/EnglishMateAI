from fastapi import Request, HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.responses import Response
import json


class RequestSizeLimitMiddleware:
    """
    请求体大小限制中间件
    防止过大的请求体导致服务器资源耗尽
    """
    
    def __init__(self, app: ASGIApp, max_size: int):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        received_body = b""
        
        async def wrapped_receive() -> dict:
            nonlocal received_body
            message = await receive()
            
            if message["type"] == "http.request":
                body = message.get("body", b"")
                received_body += body
                
                # 检查累积的请求体大小
                if len(received_body) > self.max_size:
                    raise HTTPException(
                        status_code=413,
                        detail=f"请求体过大，最大允许 {self.max_size} 字节"
                    )
                
                # 如果是最后一个请求块
                if not message.get("more_body", False):
                    # 检查完整请求体大小
                    if len(received_body) > self.max_size:
                        raise HTTPException(
                            status_code=413,
                            detail=f"请求体过大，最大允许 {self.max_size} 字节"
                        )
            
            return message

        await self.app(scope, wrapped_receive, send)


def get_request_size_limit_middleware(max_size: int):
    """
    获取请求体大小限制中间件
    """
    return lambda app: RequestSizeLimitMiddleware(app, max_size)
