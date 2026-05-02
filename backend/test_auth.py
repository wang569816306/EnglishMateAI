#!/usr/bin/env python3
"""
JWT认证功能测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:8000/ai"

def test_register():
    """测试注册"""
    print("\n📝 测试1: 用户注册")
    url = f"{BASE_URL}/auth/register"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "123456",
        "full_name": "测试用户"
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ 注册成功")
        return response.json()["data"]
    else:
        print("❌ 注册失败")
        return None


def test_login(username, password):
    """测试登录"""
    print(f"\n🔐 测试2: 用户登录 ({username})")
    url = f"{BASE_URL}/auth/login"
    data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 登录成功")
        print(f"Access Token: {result['data']['access_token'][:50]}...")
        return result["data"]
    else:
        print(f"❌ 登录失败: {response.json()}")
        return None


def test_get_me(token):
    """测试获取用户信息"""
    print("\n👤 测试3: 获取当前用户信息")
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 获取成功")
        print(f"用户信息: {json.dumps(response.json()['data'], indent=2, ensure_ascii=False)}")
    else:
        print(f"❌ 获取失败: {response.json()}")


def test_chat_with_auth(token):
    """测试聊天接口（需要认证）"""
    print("\n💬 测试4: AI聊天（JWT认证）")
    url = f"{BASE_URL}/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "question": "Hello, how are you?",
        "session_id": "test_session"
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 聊天成功")
        answer = response.json()["data"]
        print(f"AI回答: {answer[:100]}...")
    else:
        print(f"❌ 聊天失败: {response.json()}")


def test_chat_without_auth():
    """测试聊天接口（无认证，应该失败）"""
    print("\n🚫 测试5: AI聊天（无认证，应失败）")
    url = f"{BASE_URL}/chat"
    data = {
        "question": "Hello",
        "session_id": "test_session"
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ 正确拒绝未认证请求")
    else:
        print(f"❌ 应该返回401，实际返回: {response.status_code}")


def test_refresh_token(refresh_token):
    """测试刷新Token"""
    print("\n🔄 测试6: 刷新Token")
    url = f"{BASE_URL}/auth/refresh"
    data = {
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, json=data)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Token刷新成功")
        new_token = response.json()["data"]["access_token"]
        print(f"新Token: {new_token[:50]}...")
        return new_token
    else:
        print(f"❌ 刷新失败: {response.json()}")
        return None


def main():
    print("=" * 60)
    print("🧪 EnglishMateAI JWT认证功能测试")
    print("=" * 60)
    
    # 测试注册
    register_data = test_register()
    
    if register_data:
        access_token = register_data["access_token"]
        refresh_token = register_data["refresh_token"]
        
        # 测试获取用户信息
        test_get_me(access_token)
        
        # 测试聊天（有认证）
        test_chat_with_auth(access_token)
        
        # 测试聊天（无认证）
        test_chat_without_auth()
        
        # 测试刷新Token
        new_token = test_refresh_token(refresh_token)
        
        if new_token:
            # 使用新Token测试
            test_get_me(new_token)
    
    # 测试登录
    login_data = test_login("testuser", "123456")
    
    if login_data:
        test_chat_with_auth(login_data["access_token"])
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到服务器")
        print("请确保后端服务已启动: python main.py")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
