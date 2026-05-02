from fastapi import APIRouter
from .health import router as health_router
from .chat import router as chat_router
from .chat_stream import router as chat_stream_router
from .auth import router as auth_router
from .sessions import router as sessions_router
from .suggested_questions import router as suggested_questions_router
from app.core.middlewares.response_middleware import UniformResponse

api_router = APIRouter(
    prefix="/ai",
    tags=["AI 问答"],
    route_class=UniformResponse
)

# 注册所有子路由
api_router.include_router(health_router)
api_router.include_router(auth_router)  # 认证路由
api_router.include_router(chat_router)
api_router.include_router(chat_stream_router)
api_router.include_router(sessions_router)  # 会话管理路由
api_router.include_router(suggested_questions_router)  # 推荐问题路由