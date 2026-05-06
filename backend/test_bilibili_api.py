#!/usr/bin/env python3
"""
测试B站视频解析和下载接口
"""
import sys
import os
import requests
import json
sys.path.insert(0, os.path.dirname(__file__))

# 后端服务地址
BASE_URL = "http://localhost:8000"
API_PREFIX = "/ai"

def test_parse_bilibili_video():
    """测试B站视频解析接口"""
    print("=" * 60)
    print("🎬 测试1: B站视频解析接口")
    print("=" * 60)
    
    # 测试URL - 使用一个公开的B站视频
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    try:
        print(f"\n🔗 正在解析: {test_url}")
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/videos/parse",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 解析成功!")
            print(f"📺 标题: {data['data']['title']}")
            print(f"👤 上传者: {data['data']['uploader']}")
            print(f"⏱️ 时长: {data['data']['duration_string']}")
            print(f"🌐 平台: {data['data']['platform']}")
            print(f"📋 可用格式数量: {len(data['data']['formats'])}")
            
            if data['data']['formats']:
                print("\n前3个可用格式:")
                for i, fmt in enumerate(data['data']['formats'][:3], 1):
                    print(f"  {i}. {fmt['label']} (ID: {fmt['format_id']})")
            
            return True, data['data']
        else:
            print(f"❌ 解析失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False, None


def test_download_bilibili_video(video_info):
    """测试B站视频下载接口"""
    print("\n" + "=" * 60)
    print("📥 测试2: B站视频下载接口")
    print("=" * 60)
    
    if not video_info or not video_info.get('formats'):
        print("❌ 没有可用的视频信息进行下载测试")
        return False
    
    # 选择一个合适的格式进行下载（选择第一个有音频的格式）
    selected_format = None
    for fmt in video_info['formats']:
        if fmt.get('has_audio'):
            selected_format = fmt
            break
    
    if not selected_format:
        # 如果没有找到有音频的格式，使用第一个
        selected_format = video_info['formats'][0]
    
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    try:
        print(f"\n🔗 准备下载: {test_url}")
        print(f"📋 选择格式: {selected_format['label']}")
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/videos/download",
            json={
                "url": test_url,
                "format_id": selected_format['format_id']
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 下载成功!")
            print(f"📺 标题: {data['data']['title']}")
            print(f"📁 文件名: {data['data']['filename']}")
            print(f"🔗 下载链接: {data['data']['download_url']}")
            print(f"📂 文件路径: {data['data']['filepath']}")
            
            # 检查文件是否真的存在
            if os.path.exists(data['data']['filepath']):
                file_size = os.path.getsize(data['data']['filepath'])
                print(f"💾 文件大小: {file_size / (1024*1024):.2f} MB")
                print(f"✅ 文件已保存到本地")
            else:
                print(f"⚠️  文件不存在于指定路径")
            
            return True
        else:
            print(f"❌ 下载失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def test_direct_url_bilibili_video():
    """测试B站视频直链接口"""
    print("\n" + "=" * 60)
    print("🔗 测试3: B站视频直链接口")
    print("=" * 60)
    
    test_url = "https://www.bilibili.com/video/BV1GJ411x7h7"
    
    try:
        print(f"\n🔗 获取直链: {test_url}")
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/videos/direct-url",
            json={
                "url": test_url,
                "format_id": "best[ext=mp4]/best"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 直链获取成功!")
            print(f"🔗 直链地址: {data['data']['direct_url'][:100]}...")
            print(f"📄 文件格式: {data['data']['ext']}")
            print(f"📺 视频标题: {data['data']['title']}")
            return True
        else:
            print(f"❌ 直链获取失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False


def main():
    """主测试函数"""
    print("\n🚀 开始测试B站视频接口\n")
    
    # 首先测试解析
    parse_success, video_info = test_parse_bilibili_video()
    
    if parse_success:
        # 如果解析成功，测试下载
        download_success = test_download_bilibili_video(video_info)
        
        # 测试直链
        direct_url_success = test_direct_url_bilibili_video()
        
        # 总结
        print("\n" + "=" * 60)
        print("📊 测试总结")
        print("=" * 60)
        print(f"视频解析: {'✅ 通过' if parse_success else '❌ 失败'}")
        print(f"视频下载: {'✅ 通过' if download_success else '❌ 失败'}")
        print(f"直链获取: {'✅ 通过' if direct_url_success else '❌ 失败'}")
        
        if parse_success and download_success:
            print("\n🎉 B站视频功能测试完成！")
        else:
            print("\n⚠️  部分测试失败，请检查网络连接或稍后重试")
    else:
        print("\n❌ 解析失败，无法继续后续测试")
        print("请确保:")
        print("1. 后端服务正在运行 (python main.py)")
        print("2. 网络连接正常")
        print("3. B站视频链接有效")


if __name__ == "__main__":
    main()