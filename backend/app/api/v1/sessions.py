"""
会话管理API路由
提供会话列表、创建会话、加载会话消息等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import Session as SessionModel, Message as MessageModel
from app.auth.jwt_auth import get_current_user
from app.schemas.response import ApiResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/sessions", tags=["会话管理"])


class SessionResponse(BaseModel):
    """会话响应模型"""
    id: int
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """消息响应模型"""
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/list")
async def get_session_list(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的历史会话列表
    
    Returns:
        会话列表，按更新时间倒序排列
    """
    sessions = db.query(SessionModel).filter(
        SessionModel.user_id == current_user["id"]
    ).order_by(
        SessionModel.updated_at.desc()
    ).all()
    
    # 转换为字典列表
    session_list = [
        {
            "id": s.id,
            "session_id": s.session_id,
            "title": s.title,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None
        }
        for s in sessions
    ]
    
    return ApiResponse(code=200, msg="成功", data=session_list)


@router.post("/create")
async def create_session(
    session_data: dict = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新会话
    
    Args:
        session_data: 包含title的可选数据
        
    Returns:
        创建的会话信息
    """
    import uuid
    
    # 生成唯一的session_id
    new_session_id = f"session_{uuid.uuid4().hex[:12]}"
    
    # 获取标题（如果有）
    title = session_data.get("title", "新对话") if session_data else "新对话"
    
    # 创建会话记录
    new_session = SessionModel(
        user_id=current_user["id"],
        session_id=new_session_id,
        title=title
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    # 转换为字典
    session_dict = {
        "id": new_session.id,
        "session_id": new_session.session_id,
        "title": new_session.title,
        "created_at": new_session.created_at.isoformat() if new_session.created_at else None,
        "updated_at": new_session.updated_at.isoformat() if new_session.updated_at else None
    }
    
    return ApiResponse(code=200, msg="成功", data=session_dict)


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定会话的所有消息
    
    Args:
        session_id: 会话ID
        
    Returns:
        消息列表，按时间顺序排列
    """
    # 先查找会话，确保属于当前用户
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    # 获取该会话的所有消息
    messages = db.query(MessageModel).filter(
        MessageModel.session_id == session.id
    ).order_by(
        MessageModel.created_at.asc()
    ).all()
    
    # 转换为字典列表
    message_list = [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat() if m.created_at else None
        }
        for m in messages
    ]
    
    return ApiResponse(code=200, msg="成功", data=message_list)


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除指定会话及其所有消息
    
    Args:
        session_id: 会话ID
        
    Returns:
        删除结果
    """
    # 查找会话
    session = db.query(SessionModel).filter(
        SessionModel.session_id == session_id,
        SessionModel.user_id == current_user["id"]
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或无权访问")
    
    # 删除该会话的所有消息
    db.query(MessageModel).filter(
        MessageModel.session_id == session.id
    ).delete()
    
    # 删除会话
    db.delete(session)
    db.commit()
    
    return ApiResponse(code=200, msg="成功", data={"message": "会话已删除"})
