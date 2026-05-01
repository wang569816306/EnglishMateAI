from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse  # 关键
from app.schemas.chat import ChatRequest
from app.agents.chat_agent_stream import chat_agent_stream
from app.auth.api_key_auth import verify_api_key

router = APIRouter()


@router.post("/chat_stream")
async def ai_chat_stream(
        request: ChatRequest,
        user_info: dict = Depends(verify_api_key)  # 添加 API Key 认证
):
    """
    AI 流式聊天接口（需要 API Key 认证）
    
    Args:
        request: 聊天请求，包含问题和会话ID
        user_info: 从 API Key 解析的用户信息
        
    Returns:
        流式响应（SSE格式）
    """
    session_id = request.session_id or "default"
    # 直接返回流式响应
    return StreamingResponse(
        chat_agent_stream(request.question, session_id),
        media_type="text/event-stream",  # 必须改这个！
        headers={
            "Cache-Control": "no-cache",  # 禁止缓存
            "Connection": "keep-alive",  # 保持连接
            "X-Accel-Buffering": "no",  # Nginx禁用缓冲
        }
    )
