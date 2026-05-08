#!/usr/bin/env python3
"""
测试流式 Tool Calling 功能
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000/ai"

def login():
    """登录获取 token"""
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "test",
            "password": "test123"
        })
        if response.status_code == 200:
            data = response.json()
            return data["data"]["access_token"]
    except Exception as e:
        print(f"❌ 登录失败: {e}")
    return None

def test_stream_with_tools(token):
    """测试流式 Tool Calling"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_cases = [
        {
            "name": "📖 测试词典查询（流式+工具）",
            "question": "serendipity 这个单词是什么意思？给我音标和例句",
        },
        {
            "name": "🔢 测试数学计算（流式+工具）",
            "question": "如果每天学30个单词，一年能学多少个？",
        },
        {
            "name": "💾 测试存储统计（流式+工具）",
            "question": "服务器下载目录还剩多少空间？",
        },
    ]
    
    print("=" * 80)
    print("🧪 流式 Tool Calling 功能测试")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   问题: {test_case['question']}")
        print(f"   回答: ", end="", flush=True)
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat_stream",
                headers=headers,
                json={
                    "question": test_case['question'], 
                    "session_id": f"stream_test_{i}",
                    "use_tools": True  # 启用工具调用
                },
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                full_answer = ""
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            content = line_str[6:]
                            
                            if content == '[DONE]':
                                break
                            elif content.startswith('[SUGGESTED_QUESTIONS]'):
                                questions = json.loads(content[21:])
                                print(f"\n   💡 推荐问题: {questions}")
                            else:
                                # 实时显示
                                print(content, end="", flush=True)
                                full_answer += content
                
                print()  # 换行
                print(f"   ✅ 状态码: {response.status_code}")
                print(f"   📊 回答长度: {len(full_answer)} 字符")
            else:
                print(f"\n   ❌ 状态码: {response.status_code}")
                print(f"   错误: {response.text}")
                
        except Exception as e:
            print(f"\n   ❌ 测试失败: {str(e)}")
        
        print("-" * 80)
    
    print("\n✅ 所有测试完成！")

if __name__ == "__main__":
    print("正在登录...")
    token = login()
    
    if token:
        print("✅ 登录成功\n")
        test_stream_with_tools(token)
    else:
        print("❌ 登录失败，请确保后端服务已启动且有测试用户")
        sys.exit(1)
