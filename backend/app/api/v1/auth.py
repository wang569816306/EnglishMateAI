"""
认证API路由
提供注册、登录、刷新Token等接口
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest, 
    LoginRequest, 
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    ChangePasswordRequest
)
from app.schemas.response import ApiResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_tokens,
    get_user_by_id,
    change_password
)
from app.core.jwt import verify_token, create_access_token
from app.settings import settings
from app.auth.jwt_auth import get_current_user
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register", response_model=ApiResponse)
async def register(register_data: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - **username**: 用户名（3-50个字符）
    - **email**: 邮箱地址
    - **password**: 密码（6-100个字符）
    - **full_name**: 真实姓名（可选）
    """
    user = register_user(db, register_data)
    
    # 生成token
    tokens = generate_tokens(user)
    
    return ApiResponse(
        code=200,
        msg="注册成功",
        data={
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name
            },
            **tokens
        }
    )


@router.post("/login", response_model=ApiResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - **username**: 用户名或邮箱
    - **password**: 密码
    
    返回 access_token 和 refresh_token
    """
    user = authenticate_user(db, login_data)
    tokens = generate_tokens(user)
    
    return ApiResponse(
        code=200,
        msg="登录成功",
        data={
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            },
            **tokens
        }
    )


@router.post("/refresh", response_model=ApiResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    刷新访问令牌
    
    使用 refresh_token 获取新的 access_token
    """
    try:
        # 验证refresh token
        payload = verify_token(refresh_data.refresh_token, token_type="refresh")
        user_id: int = int(payload.get("sub"))
        
        # 获取用户信息
        user = get_user_by_id(db, user_id)
        
        if not user.is_active:
            return ApiResponse(code=403, msg="账户已被禁用")
        
        # 生成新的access token
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        
        return ApiResponse(
            code=200,
            msg="刷新成功",
            data={
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        )
    except Exception as e:
        return ApiResponse(code=401, msg=str(e))


@router.get("/me", response_model=ApiResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    需要在请求头中携带有效的 access_token
    Authorization: Bearer <token>
    """
    return ApiResponse(
        code=200,
        msg="获取成功",
        data=current_user
    )


@router.post("/change-password", response_model=ApiResponse)
async def change_user_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（6-100个字符）
    
    需要登录状态
    """
    change_password(
        db=db,
        user_id=current_user["id"],
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    
    return ApiResponse(
        code=200,
        msg="密码修改成功"
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    用户登出
    
    前端应该清除本地存储的token
    后端可以在此添加token黑名单逻辑（可选）
    """
    return ApiResponse(
        code=200,
        msg="登出成功"
    )
