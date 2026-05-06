"""
测试代理下载接口
"""
import requests
import json

# 测试代理下载
url = "http://localhost:8000/ai/videos/proxy-download"
data = {
    "url": "https://www.bilibili.com/video/BV1GJ411x7h7",
    "format_id": "best"
}

print("测试代理下载接口...")
print(f"URL: {url}")
print(f"数据: {json.dumps(data, ensure_ascii=False)}")
print("-" * 80)

response = requests.post(url, json=data)
print(f"状态码: {response.status_code}")
print(f"响应头 Content-Type: {response.headers.get('Content-Type')}")
print(f"响应头 Content-Disposition: {response.headers.get('Content-Disposition')}")
print(f"响应内容: {response.text[:200]}")
