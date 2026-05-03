#!/usr/bin/env python3
"""
测试数据完整性脚本
检查用户、会话、消息、场景和对话数据
"""
import requests
import json

BASE_URL = "http://localhost:8000/ai"

def test_data_integrity():
    # 登录获取token
    login_data = {'username': 'newuser2026', 'password': 'test123456'}
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.status_code}")
        print(response.text)
        return
    
    print("✅ 登录成功")
    token = response.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试1: 获取会话列表
    print("\n" + "="*60)
    print("📋 测试1: 获取历史对话列表")
    print("="*60)
    sessions_resp = requests.get(f'{BASE_URL}/sessions/list', headers=headers)
    if sessions_resp.status_code == 200:
        sessions = sessions_resp.json().get('data', [])
        print(f"✅ 找到 {len(sessions)} 个会话")
        for i, session in enumerate(sessions[:3], 1):
            print(f"  {i}. ID: {session['id']}, SessionID: {session['session_id']}")
            print(f"     标题: {session['title']}")
            print(f"     创建时间: {session['created_at']}")
    else:
        print(f"❌ 获取会话列表失败: {sessions_resp.status_code}")
        print(sessions_resp.text)
    
    # 测试2: 获取口语训练对话列表
    print("\n" + "="*60)
    print("🎤 测试2: 获取口语训练历史列表")
    print("="*60)
    dialogues_resp = requests.get(f'{BASE_URL}/scenarios/dialogues', headers=headers)
    if dialogues_resp.status_code == 200:
        dialogues = dialogues_resp.json().get('data', [])
        print(f"✅ 找到 {len(dialogues)} 个对话")
        for i, dialogue in enumerate(dialogues[:3], 1):
            print(f"  {i}. ID: {dialogue['id']}")
            print(f"     标题: {dialogue['title']}")
            print(f"     场景ID: {dialogue['scenario_id']}")
            print(f"     创建时间: {dialogue['created_at']}")
            print(f"     对话轮数: {len(dialogue['dialogue_data'])}")
    else:
        print(f"❌ 获取对话列表失败: {dialogues_resp.status_code}")
        print(dialogues_resp.text)
    
    # 测试3: 获取场景列表
    print("\n" + "="*60)
    print("📄 测试3: 获取场景库列表")
    print("="*60)
    scenarios_resp = requests.get(f'{BASE_URL}/scenarios/list', headers=headers)
    if scenarios_resp.status_code == 200:
        scenarios = scenarios_resp.json().get('data', [])
        print(f"✅ 找到 {len(scenarios)} 个场景")
        for i, scenario in enumerate(scenarios[:3], 1):
            print(f"  {i}. ID: {scenario['id']}")
            print(f"     标题: {scenario['title']}")
            print(f"     文件名: {scenario.get('file_name', 'N/A')}")
            print(f"     创建时间: {scenario['created_at']}")
    else:
        print(f"❌ 获取场景列表失败: {scenarios_resp.status_code}")
        print(scenarios_resp.text)
    
    # 测试4: 获取某个会话的消息
    print("\n" + "="*60)
    print("💬 测试4: 获取会话消息")
    print("="*60)
    if sessions and len(sessions) > 0:
        first_session_id = sessions[0]['session_id']
        messages_resp = requests.get(f'{BASE_URL}/sessions/{first_session_id}/messages', headers=headers)
        if messages_resp.status_code == 200:
            messages = messages_resp.json().get('data', [])
            print(f"✅ 会话 {first_session_id} 有 {len(messages)} 条消息")
            for i, msg in enumerate(messages[:2], 1):
                print(f"  {i}. 角色: {msg['role']}")
                print(f"     内容: {msg['content'][:50]}...")
        else:
            print(f"❌ 获取消息失败: {messages_resp.status_code}")
            print(messages_resp.text)
    else:
        print("⚠️  没有会话可测试")
    
    print("\n" + "="*60)
    print("✅ 数据完整性测试完成")
    print("="*60)

if __name__ == "__main__":
    test_data_integrity()
