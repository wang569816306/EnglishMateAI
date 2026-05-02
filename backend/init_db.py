#!/usr/bin/env python3
"""
数据库初始化脚本
运行此脚本创建数据库表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import init_db, engine
from app.models.user import User, Session, Message


def main():
    print("🗄️  开始初始化数据库...")
    
    try:
        # 创建所有表
        init_db()
        print("✅ 数据库表创建成功！")
        print(f"📍 数据库位置: {engine.url}")
        
        # 显示创建的表
        from app.core.database import Base
        tables = Base.metadata.tables.keys()
        print(f"\n📋 已创建的表:")
        for table in tables:
            print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
