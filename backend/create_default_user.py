#!/usr/bin/env python3
"""
创建默认测试用户
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def create_default_user():
    """创建默认测试用户"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在admin用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        
        if existing_user:
            print("✅ admin用户已存在")
            print(f"   用户名: {existing_user.username}")
            print(f"   邮箱: {existing_user.email}")
            return
        
        # 创建默认管理员用户
        admin_user = User(
            username="admin",
            email="admin@englishmate.ai",
            hashed_password=hash_password("admin123"),
            full_name="Administrator",
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ 默认管理员用户创建成功!")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
        print(f"   邮箱: admin@englishmate.ai")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_default_user()
