"""
推荐问题API路由
提供获取英语学习相关的推荐问题
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import SuggestedQuestion
from app.schemas.response import ApiResponse

router = APIRouter(prefix="/suggested-questions", tags=["推荐问题"])


@router.get("/list")
async def get_suggested_questions(
    db: Session = Depends(get_db)
):
    """
    获取推荐的英语学习问题列表
    
    Returns:
        推荐问题列表
    """
    questions = db.query(SuggestedQuestion).filter(
        SuggestedQuestion.is_active == True
    ).order_by(
        SuggestedQuestion.sort_order.asc(),
        SuggestedQuestion.id.asc()
    ).limit(10).all()
    
    # 转换为字典列表
    question_list = [
        {
            "id": q.id,
            "question": q.question,
            "category": q.category
        }
        for q in questions
    ]
    
    return ApiResponse(code=200, msg="成功", data=question_list)
