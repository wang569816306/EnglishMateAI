#!/usr/bin/env python3
"""
测试下载频率限制功能
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/ai"

def test_rate_limit():
    """测试频率限制"""
    print("🧪 开始测试下载频率限制...")
    print("=" * 60)
    
    # 先查看当前存储状态
    print("\n1️⃣  查看存储统计:")
    response = requests.get(f"{BASE_URL}/videos/storage-stats")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    if data["code"] == 200:
        stats = data["data"]
        print(f"   文件大小: {stats['total_size_mb']:.2f}MB")
        print(f"   文件数量: {stats['file_count']}")
        print(f"   使用率: {stats['usage_percent']:.2f}%")
    
    # 测试清理接口
    print("\n2️⃣  测试手动清理:")
    response = requests.post(f"{BASE_URL}/videos/cleanup")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    if data["code"] == 200:
        cleanup = data["data"]
        print(f"   时间清理: {cleanup['time_based_cleanup']['cleaned_count']} 个文件")
        print(f"   大小清理: {cleanup['size_based_cleanup']['reason']}")
    
    print("\n✅ 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_rate_limit()
