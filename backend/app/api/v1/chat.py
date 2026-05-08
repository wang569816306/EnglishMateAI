from fastapi import APIRouter, Depends
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.chat_agent import chat_agent
from app.agents.chat_agent_with_tools import chat_agent_with_tools
from app.schemas.response import ApiResponse
from app.auth.jwt_auth import get_current_user

router = APIRouter()


@router.post("/chat", response_model=ApiResponse)
async def ai_chat(
        request: ChatRequest,
        current_user: dict = Depends(get_current_user)  # JWT认证
):
    """
    AI 聊天接口（需要 JWT 认证）
    
    Args:
        request: 聊天请求，包含问题和会话ID
        current_user: 当前登录用户信息
        
    Returns:
        AI 回答
    """
    session_id = request.session_id or f"user_{current_user['id']}_default"
    
    # 根据 use_tools 参数选择 Agent
    if request.use_tools:
        print('🔧 [Tool Calling]', session_id, 'User:', current_user['username'])
        answer = await chat_agent_with_tools(request.question, session_id)
        return ApiResponse(code=200, msg="成功（带工具调用）", data=answer)
    else:
        print('-----', session_id, 'User:', current_user['username'])
        answer = await chat_agent(request.question, session_id)
        return ApiResponse(code=200, msg="成功", data=answer)
