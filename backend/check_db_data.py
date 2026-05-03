#!/usr/bin/env python3
"""
检查数据库中的数据完整性
"""
from app.core.database import SessionLocal
from app.models.user import User, Session as SessionModel, Message, Scenario, Dialogue
import json

def check_database():
    db = SessionLocal()
    
    print("="*60)
    print("📊 数据库数据完整性检查")
    print("="*60)
    
    # 1. 检查用户
    print("\n👤 用户列表:")
    users = db.query(User).all()
    for user in users:
        print(f"  - ID: {user.id}, Username: {user.username}, Email: {user.email}")
    
    if not users:
        print("  ⚠️  没有用户数据")
        return
    
    # 选择第一个用户进行检查
    test_user = users[0]
    print(f"\n🔍 检查用户 '{test_user.username}' (ID: {test_user.id}) 的数据:\n")
    
    # 2. 检查会话
    print("📋 历史对话 (Sessions):")
    sessions = db.query(SessionModel).filter(SessionModel.user_id == test_user.id).all()
    print(f"  总数: {len(sessions)}")
    for i, session in enumerate(sessions[:3], 1):
        print(f"  {i}. ID: {session.id}, SessionID: {session.session_id}")
        print(f"     标题: {session.title}")
        print(f"     创建时间: {session.created_at}")
        
        # 检查该会话的消息
        messages = db.query(Message).filter(Message.session_id == session.id).all()
        print(f"     消息数: {len(messages)}")
    
    if not sessions:
        print("  ⚠️  没有会话数据")
    
    # 3. 检查场景
    print("\n📄 场景库 (Scenarios):")
    scenarios = db.query(Scenario).filter(Scenario.user_id == test_user.id).all()
    print(f"  总数: {len(scenarios)}")
    for i, scenario in enumerate(scenarios[:3], 1):
        print(f"  {i}. ID: {scenario.id}")
        print(f"     标题: {scenario.title}")
        print(f"     文件名: {scenario.file_name}")
        print(f"     创建时间: {scenario.created_at}")
    
    if not scenarios:
        print("  ⚠️  没有场景数据")
    
    # 4. 检查对话
    print("\n🎤 口语训练对话 (Dialogues):")
    dialogues = db.query(Dialogue).filter(Dialogue.user_id == test_user.id).all()
    print(f"  总数: {len(dialogues)}")
    for i, dialogue in enumerate(dialogues[:3], 1):
        print(f"  {i}. ID: {dialogue.id}")
        print(f"     标题: {dialogue.title}")
        print(f"     场景ID: {dialogue.scenario_id}")
        print(f"     创建时间: {dialogue.created_at}")
        
        # 解析对话数据
        try:
            dialogue_data = json.loads(dialogue.dialogue_data)
            print(f"     对话轮数: {len(dialogue_data)}")
            if len(dialogue_data) > 0:
                first_line = dialogue_data[0]
                print(f"     第一句: [{first_line.get('speaker', 'N/A')}] {first_line.get('text', '')[:50]}")
        except Exception as e:
            print(f"     ⚠️  对话数据解析失败: {e}")
    
    if not dialogues:
        print("  ⚠️  没有对话数据")
    
    print("\n" + "="*60)
    print("✅ 数据库检查完成")
    print("="*60)
    
    db.close()

if __name__ == "__main__":
    check_database()
