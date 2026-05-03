"""
文档管理API路由
提供文档上传、解析功能
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.jwt_auth import get_current_user
from app.schemas.response import ApiResponse
from app.services.document_parser import DocumentParser
from app.models.user import Scenario as ScenarioModel
import os

router = APIRouter(prefix="/documents", tags=["文档管理"])

# 允许的文件类型
ALLOWED_EXTENSIONS = {'.doc', '.docx', '.xls', '.xlsx'}
ALLOWED_MIME_TYPES = {
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}
# 最大文件大小 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def get_file_type(filename: str) -> str:
    """
    根据文件名判断文件类型
    
    Args:
        filename: 文件名
        
    Returns:
        文件类型 (word/excel)
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.doc', '.docx']:
        return 'word'
    elif ext in ['.xls', '.xlsx']:
        return 'excel'
    else:
        raise ValueError(f"不支持的文件类型: {ext}")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传并解析文档
    
    Args:
        file: 上传的文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        解析后的文本内容
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 检查文件大小
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"文件大小超过限制（最大{MAX_FILE_SIZE // 1024 // 1024}MB）"
        )
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    try:
        # 判断文件类型
        file_type = get_file_type(file.filename)
        
        # 解析文档
        content = DocumentParser.parse(file_content, file_type)
        
        # 检查解析结果
        if not content or not content.strip():
            raise ValueError("文档内容为空")
        
        return ApiResponse(
            code=200, 
            msg="文档解析成功", 
            data={
                "content": content,
                "file_name": file.filename,
                "file_type": file_type,
                "file_size": len(file_content)
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")


@router.post("/upload-and-save")
async def upload_and_save_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传、解析并保存为场景
    
    Args:
        file: 上传的文件
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        解析后的文本内容和场景ID
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {'.doc', '.docx', '.xls', '.xlsx'}:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件类型，仅支持: .doc, .docx, .xls, .xlsx"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 检查文件大小
    if len(file_content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="文件大小超过限制（最大10MB）")
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="文件内容为空")
    
    try:
        # 判断文件类型
        file_type = 'word' if ext in ['.doc', '.docx'] else 'excel'
        
        # 解析文档
        content = DocumentParser.parse(file_content, file_type)
        
        if not content or not content.strip():
            raise ValueError("文档内容为空")
        
        # 保存为场景
        new_scenario = ScenarioModel(
            user_id=current_user["id"],
            title=file.filename,
            content=content,
            file_name=file.filename,
            file_type=file_type
        )
        
        db.add(new_scenario)
        db.commit()
        db.refresh(new_scenario)
        
        return ApiResponse(
            code=200, 
            msg="文档解析并保存成功", 
            data={
                "scenario_id": new_scenario.id,
                "content": content,
                "file_name": file.filename,
                "file_type": file_type,
                "file_size": len(file_content)
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")
