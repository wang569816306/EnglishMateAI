"""
测试Token过期时是否正确返回401
"""
import requests
import time
import jwt
from datetime import datetime, timedelta
from app.settings import settings

# 后端API地址
BASE_URL = "http://localhost:8000/ai"

def test_expired_token():
    """测试过期Token"""
    print("=" * 60)
    print("测试1: 使用过期的Token访问需要认证的接口")
    print("=" * 60)
    
    # 创建一个已过期的token
    expired_payload = {
        "sub": "1",
        "username": "testuser",
        "type": "access",
        "exp": datetime.utcnow() - timedelta(hours=1)  # 1小时前过期
    }
    
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # 使用过期token请求需要认证的接口
    headers = {
        "Authorization": f"Bearer {expired_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/sessions/list", headers=headers)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 401:
            print("\n✅ 测试通过: 正确返回401状态码")
            data = response.json()
            if data.get('code') == 401:
                print("✅ 测试通过: 响应中包含code=401")
            else:
                print(f"❌ 测试失败: 响应中code={data.get('code')}")
        else:
            print(f"\n❌ 测试失败: 期望401，实际返回{response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def test_invalid_token():
    """测试无效Token"""
    print("\n" + "=" * 60)
    print("测试2: 使用无效的Token访问需要认证的接口")
    print("=" * 60)
    
    invalid_token = "invalid.token.here"
    
    headers = {
        "Authorization": f"Bearer {invalid_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/sessions/list", headers=headers)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 401:
            print("\n✅ 测试通过: 正确返回401状态码")
            data = response.json()
            if data.get('code') == 401:
                print("✅ 测试通过: 响应中包含code=401")
            else:
                print(f"❌ 测试失败: 响应中code={data.get('code')}")
        else:
            print(f"\n❌ 测试失败: 期望401，实际返回{response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def test_no_token():
    """测试没有Token"""
    print("\n" + "=" * 60)
    print("测试3: 不提供Token访问需要认证的接口")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/sessions/list")
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 401:
            print("\n✅ 测试通过: 正确返回401状态码")
            data = response.json()
            if data.get('code') == 401:
                print("✅ 测试通过: 响应中包含code=401")
            else:
                print(f"❌ 测试失败: 响应中code={data.get('code')}")
        else:
            print(f"\n❌ 测试失败: 期望401，实际返回{response.status_code}")
            
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


if __name__ == "__main__":
    print("\n🧪 开始测试Token过期处理\n")
    
    test_expired_token()
    test_invalid_token()
    test_no_token()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
