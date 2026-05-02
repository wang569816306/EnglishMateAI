"""
认证服务层
处理用户注册、登录等业务逻辑
"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, create_refresh_token
from app.settings import settings
from app.core.exceptions import APIException
from datetime import timedelta


def register_user(db: Session, user_data: RegisterRequest) -> User:
    """
    用户注册
    
    Args:
        db: 数据库会话
        user_data: 注册数据
        
    Returns:
        创建的用户对象
        
    Raises:
        APIException: 用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise APIException(code=400, msg="用户名已被注册")
        else:
            raise APIException(code=400, msg="邮箱已被注册")
    
    # 创建新用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, login_data: LoginRequest) -> User:
    """
    用户认证
    
    Args:
        db: 数据库会话
        login_data: 登录数据
        
    Returns:
        认证成功的用户对象
        
    Raises:
        APIException: 用户名或密码错误
    """
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == login_data.username) | (User.email == login_data.username)
    ).first()
    
    if not user:
        raise APIException(code=401, msg="用户名或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, user.hashed_password):
        raise APIException(code=401, msg="用户名或密码错误")
    
    # 检查账户状态
    if not user.is_active:
        raise APIException(code=403, msg="账户已被禁用")
    
    return user


def generate_tokens(user: User) -> dict:
    """
    生成访问令牌和刷新令牌
    
    Args:
        user: 用户对象
        
    Returns:
        包含token的字典
    """
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "username": user.username}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    根据ID获取用户
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        
    Returns:
        用户对象
        
    Raises:
        APIException: 用户不存在
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise APIException(code=404, msg="用户不存在")
    return user


def get_user_by_username(db: Session, username: str) -> User:
    """
    根据用户名获取用户
    
    Args:
        db: 数据库会话
        username: 用户名
        
    Returns:
        用户对象
    """
    return db.query(User).filter(User.username == username).first()


def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
    """
    修改密码
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        old_password: 旧密码
        new_password: 新密码
        
    Returns:
        是否成功
        
    Raises:
        APIException: 旧密码错误或用户不存在
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise APIException(code=404, msg="用户不存在")
    
    # 验证旧密码
    if not verify_password(old_password, user.hashed_password):
        raise APIException(code=401, msg="旧密码错误")
    
    # 更新密码
    user.hashed_password = hash_password(new_password)
    db.commit()
    
    return True
