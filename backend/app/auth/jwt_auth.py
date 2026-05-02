"""
JWT认证依赖
用于保护需要登录的API端点
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import verify_token
from app.services.auth_service import get_user_by_id
from app.core.database import get_db
from sqlalchemy.orm import Session

# 创建HTTP Bearer安全方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    获取当前登录用户
    
    Args:
        credentials: HTTP认证凭证
        db: 数据库会话
        
    Returns:
        用户信息字典
        
    Raises:
        HTTPException: Token无效或用户不存在
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # 验证access token
        payload = verify_token(token, token_type="access")
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库获取用户
    user = get_user_by_id(db, user_id)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url
    }


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    获取当前活跃用户（额外的活跃度检查）
    
    Args:
        current_user: 当前用户信息
        
    Returns:
        用户信息字典
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )
    return current_user
