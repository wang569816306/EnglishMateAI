"""
测试视频下载API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.video_downloader import VideoDownloader

def test_parse_video():
    """测试视频解析功能"""
    print("=" * 60)
    print("测试1: 解析YouTube视频")
    print("=" * 60)
    
    downloader = VideoDownloader()
    
    # 测试URL（一个公开的YouTube视频）
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"\n🔗 解析链接: {test_url}")
        info = downloader.parse_video(test_url)
        
        print(f"\n✅ 解析成功!")
        print(f"📺 标题: {info['title']}")
        print(f"👤 上传者: {info['uploader']}")
        print(f"⏱️ 时长: {info['duration_string']}")
        print(f"🌐 平台: {info['platform']}")
        print(f"📝 描述: {info['description'][:100]}...")
        print(f"\n📋 可用格式数量: {len(info['formats'])}")
        
        if info['formats']:
            print("\n前3个可用格式:")
            for i, fmt in enumerate(info['formats'][:3], 1):
                print(f"  {i}. {fmt['label']}")
        
        return True
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        return False


def test_bilibili():
    """测试B站视频解析"""
    print("\n" + "=" * 60)
    print("测试2: 解析Bilibili视频")
    print("=" * 60)
    
    downloader = VideoDownloader()
    
    # B站测试视频
    test_url = "https://www.bilibili.com/video/BV1xx411c7mD"
    
    try:
        print(f"\n🔗 解析链接: {test_url}")
        info = downloader.parse_video(test_url)
        
        print(f"\n✅ 解析成功!")
        print(f"📺 标题: {info['title']}")
        print(f"👤 上传者: {info['uploader']}")
        print(f"⏱️ 时长: {info['duration_string']}")
        print(f"🌐 平台: {info['platform']}")
        
        return True
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        print("💡 提示: B站视频可能需要Cookie或网络环境支持")
        return False


if __name__ == "__main__":
    print("\n🎬 视频下载功能测试\n")
    
    # 运行测试
    test1_passed = test_parse_video()
    test2_passed = test_bilibili()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"YouTube解析: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"Bilibili解析: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed:
        print("\n🎉 视频下载功能已就绪！")
        print("\n下一步:")
        print("1. 启动后端服务: python main.py")
        print("2. 启动前端服务: npm run dev")
        print("3. 访问 http://localhost:5173/video-download")
    else:
        print("\n⚠️  请检查网络连接和yt-dlp配置")
