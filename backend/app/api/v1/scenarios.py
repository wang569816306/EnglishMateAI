"""
场景管理API路由
提供场景库保存、列表查询、对话生成等功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import Scenario as ScenarioModel, Dialogue as DialogueModel
from app.auth.jwt_auth import get_current_user
from app.schemas.response import ApiResponse
from pydantic import BaseModel
from datetime import datetime
import json

router = APIRouter(prefix="/scenarios", tags=["场景管理"])


class ScenarioResponse(BaseModel):
    """场景响应模型"""
    id: int
    title: str
    content: str
    file_name: str | None = None
    file_type: str | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DialogueRequest(BaseModel):
    """生成对话请求"""
    scenario_id: int
    title: str | None = None


class QuickDialogueRequest(BaseModel):
    """快速生成对话请求"""
    topic: str
    title: str | None = None


class DialogueLine(BaseModel):
    """对话行"""
    speaker: str  # A 或 B
    text: str
    translation: str | None = None


class DialogueResponse(BaseModel):
    """对话响应模型"""
    id: int
    title: str
    scenario_id: int
    dialogue_data: list[dict]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/save")
async def save_scenario(
    scenario_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    保存上传的文档为场景
    
    Args:
        scenario_data: 包含 title, content, file_name, file_type
    """
    new_scenario = ScenarioModel(
        user_id=current_user["id"],
        title=scenario_data.get("title", "未命名场景"),
        content=scenario_data.get("content", ""),
        file_name=scenario_data.get("file_name"),
        file_type=scenario_data.get("file_type")
    )
    
    db.add(new_scenario)
    db.commit()
    db.refresh(new_scenario)
    
    return ApiResponse(
        code=200, 
        msg="场景保存成功", 
        data={
            "id": new_scenario.id,
            "title": new_scenario.title,
            "created_at": new_scenario.created_at.isoformat() if new_scenario.created_at else None
        }
    )


@router.get("/list")
async def get_scenario_list(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的场景列表
    """
    scenarios = db.query(ScenarioModel).filter(
        ScenarioModel.user_id == current_user["id"],
        ScenarioModel.is_active == True
    ).order_by(
        ScenarioModel.created_at.desc()
    ).all()
    
    scenario_list = [
        {
            "id": s.id,
            "title": s.title,
            "file_name": s.file_name,
            "file_type": s.file_type,
            "created_at": s.created_at.isoformat() if s.created_at else None
        }
        for s in scenarios
    ]
    
    return ApiResponse(code=200, msg="成功", data=scenario_list)


@router.post("/generate-dialogue")
async def generate_dialogue(
    request: DialogueRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    基于场景内容生成双人对话
    
    Args:
        request: 包含 scenario_id 和可选的 title
    """
    # 查找场景
    scenario = db.query(ScenarioModel).filter(
        ScenarioModel.id == request.scenario_id,
        ScenarioModel.user_id == current_user["id"]
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在或无权访问")
    
    try:
        # 使用 OpenAI 生成对话
        from langchain_openai import ChatOpenAI
        from app.settings import settings
        import re
        
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        
        prompt = f"""你是一个英语教学助手。请根据以下内容生成一个实用的双人英语对话练习。

要求：
1. 对话包含8-12轮（A和B各说4-6次）
2. 内容贴近实际生活/工作场景
3. 语言难度适中（中级英语水平）
4. 每句话都要有中文翻译

原始内容：
{scenario.content[:2000]}  # 限制内容长度

请以JSON格式返回，格式如下：
[
  {{"speaker": "A", "text": "英文句子", "translation": "中文翻译"}},
  {{"speaker": "B", "text": "英文句子", "translation": "中文翻译"}},
  ...
]

只返回JSON，不要其他内容。"""
        
        response = llm.invoke(prompt)
        content = response.content
        
        # 解析JSON
        # 清理可能的markdown格式
        content = re.sub(r'^```json\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        dialogue_data = json.loads(content)
        
        # 保存到数据库
        new_dialogue = DialogueModel(
            user_id=current_user["id"],
            scenario_id=scenario.id,
            title=request.title or f"{scenario.title} - 对话练习",
            dialogue_data=json.dumps(dialogue_data, ensure_ascii=False)
        )
        
        db.add(new_dialogue)
        db.commit()
        db.refresh(new_dialogue)
        
        return ApiResponse(
            code=200,
            msg="对话生成成功",
            data={
                "id": new_dialogue.id,
                "title": new_dialogue.title,
                "dialogue_data": dialogue_data,
                "created_at": new_dialogue.created_at.isoformat() if new_dialogue.created_at else None
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成对话失败: {str(e)}")


@router.post("/generate-from-topic")
async def generate_dialogue_from_topic(
    request: QuickDialogueRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    基于主题快速生成双人对话（不需要场景）
    
    Args:
        request: 包含 topic 和可选的 title
    """
    try:
        # 使用 OpenAI 生成对话
        from langchain_openai import ChatOpenAI
        from app.settings import settings
        import re
        
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        
        prompt = f"""你是一个英语教学助手。请根据以下主题生成一个实用的双人英语对话练习。

主题：{request.topic}

要求：
1. 对话包含8-12轮（A和B各说4-6次）
2. 内容贴近实际生活/工作场景
3. 语言难度适中（中级英语水平）
4. 每句话都要有中文翻译
5. 对话要自然、实用、贴近真实场景

请以JSON格式返回，格式如下：
[
  {{"speaker": "A", "text": "英文句子", "translation": "中文翻译"}},
  {{"speaker": "B", "text": "英文句子", "translation": "中文翻译"}},
  ...
]

只返回JSON，不要其他内容。"""
        
        response = llm.invoke(prompt)
        content = response.content
        
        # 解析JSON
        # 清理可能的markdown格式
        content = re.sub(r'^```json\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
        content = content.strip()
        
        dialogue_data = json.loads(content)
        
        # 创建临时场景（用于保存对话关联）
        temp_scenario = ScenarioModel(
            user_id=current_user["id"],
            title=request.topic,
            content=f"快速生成主题: {request.topic}",
            file_name=None,
            file_type="topic"
        )
        
        db.add(temp_scenario)
        db.flush()  # 获取ID但不提交
        
        # 保存对话到数据库
        new_dialogue = DialogueModel(
            user_id=current_user["id"],
            scenario_id=temp_scenario.id,
            title=request.title or f"{request.topic} - 对话练习",
            dialogue_data=json.dumps(dialogue_data, ensure_ascii=False)
        )
        
        db.add(new_dialogue)
        db.commit()
        db.refresh(new_dialogue)
        
        return ApiResponse(
            code=200,
            msg="对话生成成功",
            data={
                "id": new_dialogue.id,
                "title": new_dialogue.title,
                "dialogue_data": dialogue_data,
                "created_at": new_dialogue.created_at.isoformat() if new_dialogue.created_at else None
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成对话失败: {str(e)}")


@router.get("/dialogues")
async def get_dialogue_list(
    scenario_id: int | None = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取对话列表
    """
    query = db.query(DialogueModel).filter(
        DialogueModel.user_id == current_user["id"]
    )
    
    if scenario_id:
        query = query.filter(DialogueModel.scenario_id == scenario_id)
    
    dialogues = query.order_by(DialogueModel.id.desc()).all()
    
    dialogue_list = [
        {
            "id": d.id,
            "title": d.title,
            "scenario_id": d.scenario_id,
            "dialogue_data": json.loads(d.dialogue_data),
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in dialogues
    ]
    
    return ApiResponse(code=200, msg="成功", data=dialogue_list)


@router.get("/dialogues/{dialogue_id}")
async def get_dialogue_detail(
    dialogue_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单个对话详情
    """
    dialogue = db.query(DialogueModel).filter(
        DialogueModel.id == dialogue_id,
        DialogueModel.user_id == current_user["id"]
    ).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="对话不存在或无权访问")
    
    return ApiResponse(
        code=200,
        msg="成功",
        data={
            "id": dialogue.id,
            "title": dialogue.title,
            "scenario_id": dialogue.scenario_id,
            "dialogue_data": json.loads(dialogue.dialogue_data),
            "created_at": dialogue.created_at.isoformat() if dialogue.created_at else None
        }
    )


@router.put("/dialogues/{dialogue_id}")
async def update_dialogue(
    dialogue_id: int,
    request_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新对话（重命名）
    """
    dialogue = db.query(DialogueModel).filter(
        DialogueModel.id == dialogue_id,
        DialogueModel.user_id == current_user["id"]
    ).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="对话不存在或无权访问")
    
    # 更新标题
    if "title" in request_data:
        dialogue.title = request_data["title"]
        db.commit()
        db.refresh(dialogue)
    
    return ApiResponse(
        code=200,
        msg="更新成功",
        data={
            "id": dialogue.id,
            "title": dialogue.title
        }
    )


@router.delete("/dialogues/{dialogue_id}")
async def delete_dialogue(
    dialogue_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除对话
    """
    dialogue = db.query(DialogueModel).filter(
        DialogueModel.id == dialogue_id,
        DialogueModel.user_id == current_user["id"]
    ).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="对话不存在或无权访问")
    
    db.delete(dialogue)
    db.commit()
    
    return ApiResponse(code=200, msg="删除成功")


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除场景（软删除）
    """
    scenario = db.query(ScenarioModel).filter(
        ScenarioModel.id == scenario_id,
        ScenarioModel.user_id == current_user["id"]
    ).first()
    
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在或无权访问")
    
    scenario.is_active = False
    db.commit()
    
    return ApiResponse(code=200, msg="删除成功")
