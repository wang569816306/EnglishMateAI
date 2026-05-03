#!/usr/bin/env python3
"""
统一用户数据脚本
将所有数据迁移到指定的用户ID下
"""
from app.core.database import SessionLocal
from app.models.user import User, Session as SessionModel, Message, Scenario, Dialogue

def unify_user_data(target_user_id: int = 2):
    """
    将所有用户的数据迁移到目标用户ID下
    
    Args:
        target_user_id: 目标用户ID（默认为2，即newuser2026）
    """
    db = SessionLocal()
    
    try:
        # 获取目标用户
        target_user = db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            print(f"❌ 目标用户 ID={target_user_id} 不存在")
            return
        
        print("="*60)
        print(f"🔄 开始统一数据到用户 '{target_user.username}' (ID: {target_user_id})")
        print("="*60)
        
        # 获取所有其他用户
        other_users = db.query(User).filter(User.id != target_user_id).all()
        
        for user in other_users:
            print(f"\n📦 迁移用户 '{user.username}' (ID: {user.id}) 的数据:")
            
            # 1. 迁移会话
            sessions = db.query(SessionModel).filter(SessionModel.user_id == user.id).all()
            session_count = len(sessions)
            if session_count > 0:
                for session in sessions:
                    session.user_id = target_user_id
                db.commit()
                print(f"  ✅ 迁移了 {session_count} 个会话")
            else:
                print(f"  ⚪ 没有会话需要迁移")
            
            # 2. 迁移场景
            scenarios = db.query(Scenario).filter(Scenario.user_id == user.id).all()
            scenario_count = len(scenarios)
            if scenario_count > 0:
                for scenario in scenarios:
                    scenario.user_id = target_user_id
                db.commit()
                print(f"  ✅ 迁移了 {scenario_count} 个场景")
            else:
                print(f"  ⚪ 没有场景需要迁移")
            
            # 3. 迁移对话
            dialogues = db.query(Dialogue).filter(Dialogue.user_id == user.id).all()
            dialogue_count = len(dialogues)
            if dialogue_count > 0:
                for dialogue in dialogues:
                    dialogue.user_id = target_user_id
                db.commit()
                print(f"  ✅ 迁移了 {dialogue_count} 个对话")
            else:
                print(f"  ⚪ 没有对话需要迁移")
        
        # 统计最终结果
        print("\n" + "="*60)
        print("📊 最终数据统计:")
        print("="*60)
        
        final_sessions = db.query(SessionModel).filter(SessionModel.user_id == target_user_id).count()
        final_scenarios = db.query(Scenario).filter(Scenario.user_id == target_user_id).count()
        final_dialogues = db.query(Dialogue).filter(Dialogue.user_id == target_user_id).count()
        
        print(f"✅ 用户 '{target_user.username}' (ID: {target_user_id}):")
        print(f"   - 会话数: {final_sessions}")
        print(f"   - 场景数: {final_scenarios}")
        print(f"   - 对话数: {final_dialogues}")
        
        print("\n✅ 数据统一完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("⚠️  警告: 此操作将修改数据库中的数据")
    print("   将所有用户的数据迁移到 newuser2026 (ID=2)\n")
    
    confirm = input("确认继续? (yes/no): ")
    if confirm.lower() == 'yes':
        unify_user_data(target_user_id=2)
    else:
        print("❌ 操作已取消")
