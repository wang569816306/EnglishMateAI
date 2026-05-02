from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse  # 关键
from sqlalchemy.orm import Session
from app.schemas.chat import ChatRequest
from app.agents.chat_agent_stream import chat_agent_stream
from app.auth.jwt_auth import get_current_user
from app.core.database import get_db
from app.models.user import Session as SessionModel, Message as MessageModel
import uuid

router = APIRouter()


@router.post("/chat_stream")
async def ai_chat_stream(
        request: ChatRequest,
        current_user: dict = Depends(get_current_user),  # JWT认证
        db: Session = Depends(get_db)  # 数据库会话
):
    """
    AI 流式聊天接口（需要 JWT 认证）
    
    Args:
        request: 聊天请求，包含问题和会话ID
        current_user: 当前登录用户信息
        db: 数据库会话
        
    Returns:
        流式响应（SSE格式）
    """
    session_id = request.session_id or f"user_{current_user['id']}_default"
    
    # 如果session_id是默认值，创建新会话
    if not request.session_id or request.session_id == "default":
        new_session_id = f"session_{uuid.uuid4().hex[:12]}"
        # 创建会话记录
        new_session = SessionModel(
            user_id=current_user["id"],
            session_id=new_session_id,
            title=request.question[:50]  # 用第一个问题作为标题
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session_id
    else:
        # 检查会话是否存在，不存在则创建
        existing_session = db.query(SessionModel).filter(
            SessionModel.session_id == session_id,
            SessionModel.user_id == current_user["id"]
        ).first()
        
        if not existing_session:
            new_session = SessionModel(
                user_id=current_user["id"],
                session_id=session_id,
                title=request.question[:50]
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
    
    # 保存用户消息到数据库
    db_session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user["id"]
    ).first()
    
    if db_session:
        user_message = MessageModel(
            session_id=db_session.id,
            role="user",
            content=request.question
        )
        db.add(user_message)
        db.commit()
    
    # 直接返回流式响应
    return StreamingResponse(
        chat_agent_stream(request.question, session_id, db, db_session.id if db_session else None),
        media_type="text/event-stream",  # 必须改这个！
        headers={
            "Cache-Control": "no-cache",  # 禁止缓存
            "Connection": "keep-alive",  # 保持连接
            "X-Accel-Buffering": "no",  # Nginx禁用缓冲
            "X-Session-Id": session_id,  # 返回会话ID
        }
    )
