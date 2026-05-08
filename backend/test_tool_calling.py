#!/usr/bin/env python3
"""
测试 Tool Calling 功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/ai"

# 登录获取 token
def login():
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "test",
        "password": "test123"
    })
    if response.status_code == 200:
        data = response.json()
        return data["data"]["access_token"]
    return None

def test_tool_calling(token):
    """测试 Tool Calling 功能"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_cases = [
        {
            "name": "测试词典查询",
            "question": "serendipity 这个单词是什么意思？给我音标和例句",
            "expected_tool": "search_english_dictionary"
        },
        {
            "name": "测试数学计算",
            "question": "如果每天学30个单词，一年能学多少个？",
            "expected_tool": "calculate_math"
        },
        {
            "name": "测试视频解析",
            "question": "帮我看看这个视频的信息：https://www.bilibili.com/video/BV1GJ411x7h7",
            "expected_tool": "get_video_info"
        },
        {
            "name": "测试存储统计",
            "question": "服务器下载目录还剩多少空间？",
            "expected_tool": "get_storage_stats"
        },
        {
            "name": "测试普通对话（不应调用工具）",
            "question": "你好，请介绍一下你自己",
            "expected_tool": None
        }
    ]
    
    print("=" * 80)
    print("🧪 Tool Calling 功能测试")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   问题: {test_case['question'][:60]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                headers=headers,
                json={
                    "question": test_case['question'], 
                    "session_id": f"test_session_{i}",
                    "use_tools": True  # 启用工具调用
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("data", "")
                print(f"   ✅ 状态码: {response.status_code}")
                print(f"   📝 回答: {answer[:200]}...")
                
                if test_case['expected_tool']:
                    print(f"   🔧 预期调用工具: {test_case['expected_tool']}")
            else:
                print(f"   ❌ 状态码: {response.status_code}")
                print(f"   错误: {response.text}")
                
        except Exception as e:
            print(f"   ❌ 测试失败: {str(e)}")
        
        print("-" * 80)
    
    print("\n✅ 所有测试完成！")

if __name__ == "__main__":
    print("正在登录...")
    token = login()
    
    if token:
        print("✅ 登录成功\n")
        test_tool_calling(token)
    else:
        print("❌ 登录失败，请确保后端服务已启动且有测试用户")
        print("提示：可以先注册一个测试用户")
