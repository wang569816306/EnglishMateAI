from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    question: str = Field(
        ..., 
        description="用户问题", 
        min_length=1, 
        max_length=2000,
        examples=["请介绍一下人工智能的发展历史"]
    )
    session_id: Optional[str] = Field(
        "default",
        description="会话ID，用于多轮对话记忆。不传则使用默认值"
    )

class ChatResponse(BaseModel):
    status: str
    question: str
    answer: str