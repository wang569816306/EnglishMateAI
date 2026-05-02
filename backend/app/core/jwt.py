"""
JWT Token 工具类
"""
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.settings import settings
from app.core.exceptions import APIException


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据（通常包含用户ID）
        expires_delta: 过期时间增量
        
    Returns:
        JWT token字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        
    Returns:
        JWT refresh token字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict:
    """
    验证Token
    
    Args:
        token: JWT token字符串
        token_type: token类型 (access/refresh)
        
    Returns:
        解码后的payload数据
        
    Raises:
        APIException: Token无效或已过期
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        
        # 验证token类型
        if payload.get("type") != token_type:
            raise APIException(code=401, msg=f"无效的{token_type} token类型")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise APIException(code=401, msg="Token已过期")
    except jwt.InvalidTokenError:
        raise APIException(code=401, msg="无效的Token")


def decode_token(token: str) -> dict:
    """
    解码Token（不验证类型，用于通用场景）
    
    Args:
        token: JWT token字符串
        
    Returns:
        解码后的payload数据
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise APIException(code=401, msg="Token已过期")
    except jwt.InvalidTokenError:
        raise APIException(code=401, msg="无效的Token")
