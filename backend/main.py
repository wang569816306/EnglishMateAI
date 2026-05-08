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
from app.core.database import init_db
from app.services.download_manager import download_manager
import uvicorn
import sys
import asyncio

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

# 初始化数据库
init_db()
print("✅ 数据库初始化完成")

# 初始化下载管理器并执行启动时清理
print("🧹 检查下载目录...")
storage_stats = download_manager.get_storage_stats()
print(f"📊 当前存储: {storage_stats['total_size_mb']:.2f}MB / {storage_stats['max_size_gb']}GB "
      f"({storage_stats['usage_percent']:.1f}%), 文件数: {storage_stats['file_count']}")

# 如果超过80%，自动清理
if storage_stats['usage_percent'] > 80:
    print("⚠️  存储空间使用率较高，执行自动清理...")
    cleanup_result = download_manager.auto_cleanup()
    print(f"✅ 清理完成: {cleanup_result['time_based_cleanup']['cleaned_count']} 个文件, "
          f"{cleanup_result['time_based_cleanup']['cleaned_size_mb']:.2f}MB")

# 配置 CORS 跨域支持 - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源（开发环境）
    allow_credentials=True,  # 允许携带认证信息（cookies、authorization headers等）
    allow_methods=["*"],  # 允许所有 HTTP 方法（GET、POST、PUT、DELETE、OPTIONS等）
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
)

# 添加请求体大小限制中间件
app.add_middleware(RequestSizeLimitMiddleware, max_size=settings.MAX_REQUEST_SIZE)

# 挂载所有接口
app.include_router(api_router)

# 注册全局异常处理器
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # 404, 405等
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # 参数验证
app.add_exception_handler(Exception, global_exception_handler)  # 其他所有异常


@app.on_event("startup")
async def startup_event():
    """启动时执行的任务"""
    # 启动后台定时清理任务
    asyncio.create_task(scheduled_cleanup())


async def scheduled_cleanup():
    """
    定时清理任务 - 每6小时执行一次
    """
    while True:
        await asyncio.sleep(6 * 3600)  # 6小时
        try:
            print("🧹 执行定时清理任务...")
            result = download_manager.auto_cleanup()
            print(f"✅ 定时清理完成: {result['time_based_cleanup']['cleaned_count']} 个文件")
        except Exception as e:
            print(f"❌ 定时清理失败: {e}")

if __name__ == "__main__":
    print_banner()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )