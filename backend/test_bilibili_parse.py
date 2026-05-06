#!/usr/bin/env python3
"""
测试 Bilibili 视频解析（优化版）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.video_downloader import VideoDownloader

def test_bilibili_parse():
    """测试B站视频解析"""
    print("=" * 60)
    print("🎬 Bilibili 视频解析测试（优化版）")
    print("=" * 60)
    
    downloader = VideoDownloader()
    
    # 测试多个B站视频
    test_urls = [
        "https://www.bilibili.com/video/BV1GJ411x7h7",  # Rick Astley
        "https://www.bilibili.com/video/BV1xx411c7mD",  # 另一个测试视频
    ]
    
    results = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n{'='*60}")
        print(f"测试 {i}: {url}")
        print('='*60)
        
        try:
            print(f"\n⏳ 正在解析...")
            info = downloader.parse_video(url)
            
            print(f"✅ 解析成功!")
            print(f"   📺 标题: {info['title']}")
            print(f"   👤 上传者: {info['uploader']}")
            print(f"   ⏱️ 时长: {info['duration_string']}")
            print(f"   🌐 平台: {info['platform']}")
            print(f"   📋 可用格式: {len(info['formats'])} 个")
            
            if info['formats']:
                print(f"\n   前3个可用格式:")
                for j, fmt in enumerate(info['formats'][:3], 1):
                    print(f"     {j}. {fmt['label']}")
            
            results.append((url, True, None))
            
        except Exception as e:
            print(f"\n❌ 解析失败")
            print(f"   错误信息: {str(e)}")
            results.append((url, False, str(e)))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    for url, success, error in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status}: {url[:50]}...")
        if error:
            print(f"   错误: {error[:100]}")
    
    print(f"\n总计: {success_count}/{total_count} 测试通过")
    
    if success_count > 0:
        print("\n🎉 Bilibili 解析功能正常！")
        print("\n💡 提示:")
        print("   - 如果某些视频解析失败，可能是网络问题")
        print("   - B站部分视频可能需要登录或Cookie")
        print("   - 建议在稳定的网络环境下使用")
    else:
        print("\n⚠️  所有测试都失败了，请检查:")
        print("   1. 网络连接是否正常")
        print("   2. 是否需要科学上网")
        print("   3. yt-dlp 是否是最新版本")
    
    print("=" * 60 + "\n")
    
    return success_count > 0


if __name__ == "__main__":
    print("\n🚀 开始 Bilibili 视频解析测试\n")
    success = test_bilibili_parse()
    exit(0 if success else 1)
