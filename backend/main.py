from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1 import api_router
from app.settings import settings
from app.core.middlewares.exception_handler import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from app.core.middlewares.request_size_limit import RequestSizeLimitMiddleware
import uvicorn
import sys

def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════╗
║                                          ║
║   🚀  Fast-AI Service                   ║
║   FastAPI + LangChain AI Platform       ║
║                                          ║
╚══════════════════════════════════════════╝
    """
    print(banner)
    print(f"📍 服务地址: http://localhost:8000")
    print(f"📊 API文档: http://localhost:8000/docs")
    print(f"🔖 版本信息: {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    print("=" * 50)
    print()

app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION
)

# 配置 CORS 跨域支持
# 解析允许的源列表
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,  # 允许的源域名列表
    allow_credentials=True,  # 允许携带认证信息（cookies、authorization headers等）
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET、POST、PUT、DELETE等）
    allow_headers=["*"],  # 允许所有请求头
)

# 添加请求体大小限制中间件
app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_REQUEST_SIZE)

# 挂载所有接口
app.include_router(api_router)

# 注册全局异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # 404, 405等
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # 参数验证
app.add_exception_handler(Exception, global_exception_handler)  # 其他所有异常

if __name__ == "__main__":
    print_banner()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )