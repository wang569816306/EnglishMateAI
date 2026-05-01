from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.chat_agent import chat_agent
from app.schemas.response import ApiResponse
from app.auth.api_key_auth import verify_api_key

router = APIRouter()


@router.post("/chat", response_model=ApiResponse)
async def ai_chat(
        request: ChatRequest,
        user_info: dict = Depends(verify_api_key)  # 添加 API Key 认证
):
    """
    AI 聊天接口（需要 API Key 认证）
    
    Args:
        request: 聊天请求，包含问题和会话ID
        user_info: 从 API Key 解析的用户信息
        
    Returns:
        AI 回答
    """
    session_id = request.session_id or "default"
    print('-----', session_id)
    answer = await chat_agent(request.question, session_id)
    return ApiResponse(code=200, msg="成功", data=answer)
