"""
API Key 认证模块
提供基于 API Key 的身份验证功能
"""

from fastapi import Header, HTTPException, Depends
from typing import Optional
from app.settings import settings


def get_valid_api_keys() -> dict:
    """
    从配置中获取有效的 API Keys
    
    Returns:
        dict: API Key 到用户信息的映射
    """
    if not settings.API_KEY_ENABLED:
        return {}
    
    api_keys_str = settings.API_KEYS
    keys_list = [key.strip() for key in api_keys_str.split(",") if key.strip()]
    
    # 构建 API Key 字典
    valid_keys = {}
    for key in keys_list:
        valid_keys[key] = {"name": f"用户_{key[:8]}", "level": "basic"}
    
    return valid_keys


# 动态获取有效的 API Keys
VALID_API_KEYS = get_valid_api_keys()


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> dict:
    """
    验证 API Key
    
    Args:
        x_api_key: 从请求头中获取的 API Key
        
    Returns:
        dict: 用户信息
        
    Raises:
        HTTPException: 当 API Key 无效时抛出 401 错误
    """
    # 如果未启用 API Key 认证，直接返回匿名用户
    if not settings.API_KEY_ENABLED:
        return {"name": "匿名用户", "level": "guest"}
    
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="缺少 API Key，请在请求头中添加 X-API-Key"
        )
    
    # 验证 API Key
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="无效的 API Key"
        )
    
    # 返回用户信息
    return VALID_API_KEYS[x_api_key]


# 依赖项：需要认证的端点使用此依赖
get_current_user = Depends(verify_api_key)
