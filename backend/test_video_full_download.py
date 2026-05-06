#!/usr/bin/env python3
"""
测试视频完整下载流程
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.video_downloader import VideoDownloader
import time

def test_full_download():
    """测试完整的视频下载流程"""
    print("=" * 60)
    print("🎬 视频完整下载流程测试")
    print("=" * 60)
    
    downloader = VideoDownloader()
    
    # 使用一个较小的测试视频（Rick Astley - Never Gonna Give You Up）
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    print(f"\n📹 测试视频: {test_url}")
    print("\n步骤1: 解析视频信息...")
    
    try:
        # 1. 解析视频
        info = downloader.parse_video(test_url)
        print(f"✅ 解析成功")
        print(f"   标题: {info['title']}")
        print(f"   时长: {info['duration_string']}")
        print(f"   可用格式: {len(info['formats'])} 个")
        
        # 2. 选择一个合适的格式（选择中等质量以加快下载）
        # 优先选择有音频的格式
        suitable_formats = [f for f in info['formats'] if f['has_audio']]
        
        if not suitable_formats:
            print("⚠️  没有找到带音频的格式，使用第一个格式")
            suitable_formats = info['formats']
        
        # 选择一个适中的格式（不是最高清，下载更快）
        chosen_format = None
        for fmt in suitable_formats:
            if '720p' in fmt['label'] or '480p' in fmt['label']:
                chosen_format = fmt
                break
        
        if not chosen_format:
            chosen_format = suitable_formats[0]
        
        print(f"\n📋 选择的格式: {chosen_format['label']}")
        print(f"   格式ID: {chosen_format['format_id']}")
        print(f"   文件大小: {downloader._format_filesize(chosen_format.get('filesize') or chosen_format.get('filesize_approx'))}")
        
        # 3. 下载视频
        print(f"\n⏳ 开始下载视频...")
        start_time = time.time()
        
        result = downloader.download_video(test_url, chosen_format['format_id'])
        
        end_time = time.time()
        download_duration = end_time - start_time
        
        print(f"✅ 下载成功!")
        print(f"   文件名: {result['filename']}")
        print(f"   文件路径: {result['filepath']}")
        print(f"   下载耗时: {download_duration:.2f} 秒")
        
        # 4. 验证文件是否存在
        if os.path.exists(result['filepath']):
            file_size = os.path.getsize(result['filepath'])
            print(f"   文件大小: {downloader._format_filesize(file_size)}")
            print(f"   ✅ 文件验证通过")
        else:
            print(f"   ❌ 文件不存在!")
            return False
        
        print(f"\n🎉 完整下载流程测试通过!")
        print(f"\n💡 提示:")
        print(f"   - 视频已保存到: {result['filepath']}")
        print(f"   - 可通过 API 访问: /api/v1/videos/file/{result['filename']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_direct_url():
    """测试获取直链功能"""
    print("\n" + "=" * 60)
    print("🔗 测试获取视频直链")
    print("=" * 60)
    
    downloader = VideoDownloader()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"\n📹 测试视频: {test_url}")
        print("\n⏳ 获取直链...")
        
        # 先解析获取格式
        info = downloader.parse_video(test_url)
        
        # 选择一个格式
        suitable_formats = [f for f in info['formats'] if f['has_audio']]
        if suitable_formats:
            chosen_format = suitable_formats[0]
            
            result = downloader.get_direct_url(test_url, chosen_format['format_id'])
            
            print(f"✅ 直链获取成功")
            print(f"   直链URL: {result['direct_url'][:100]}...")
            print(f"   文件格式: {result['ext']}")
            print(f"   文件大小: {downloader._format_filesize(result.get('filesize'))}")
            
            return True
        else:
            print("⚠️  没有可用格式")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 开始视频下载功能完整测试\n")
    
    # 运行测试
    test1_passed = test_full_download()
    test2_passed = test_direct_url()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)
    print(f"完整下载流程: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"直链获取功能: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed:
        print("\n🎉 视频下载功能完全正常！")
    else:
        print("\n⚠️  请检查网络连接和yt-dlp配置")
    
    print("=" * 60 + "\n")
