"""
Whisper 语音评分功能测试脚本
用于验证 Whisper 是否正确安装和配置
"""
import sys
import os

def test_imports():
    """测试依赖导入"""
    print("🔍 测试依赖导入...")
    
    try:
        import whisper
        print("✅ openai-whisper 导入成功")
    except ImportError as e:
        print(f"❌ openai-whisper 导入失败: {e}")
        print("💡 请运行: pip install openai-whisper")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch 导入成功 (版本: {torch.__version__})")
    except ImportError as e:
        print(f"❌ PyTorch 导入失败: {e}")
        print("💡 请运行: pip install torch torchaudio")
        return False
    
    try:
        import ffmpeg
        print("✅ FFmpeg-python 导入成功")
    except ImportError:
        print("⚠️  FFmpeg-python 未安装（可选）")
    
    return True


def test_ffmpeg():
    """测试 FFmpeg 是否可用"""
    print("\n🔍 测试 FFmpeg...")
    
    import subprocess
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg 可用: {version_line}")
            return True
        else:
            print("❌ FFmpeg 执行失败")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg 未找到")
        print("💡 macOS: brew install ffmpeg")
        print("💡 Ubuntu: sudo apt-get install ffmpeg")
        print("💡 Windows: 从 https://ffmpeg.org/download.html 下载")
        return False
    except Exception as e:
        print(f"❌ FFmpeg 测试失败: {e}")
        return False


def test_whisper_model():
    """测试 Whisper 模型加载"""
    print("\n🔍 测试 Whisper 模型加载...")
    
    try:
        import whisper
        
        print("⏳ 正在加载 base 模型（首次使用会下载约 150MB）...")
        model = whisper.load_model("base")
        
        print("✅ 模型加载成功！")
        print(f"📦 模型大小: ~150MB")
        print(f"🎯 模型类型: base")
        
        # 显示模型信息
        print(f"\n📊 模型详情:")
        print(f"   - 维度: {model.dims}")
        print(f"   - 设备: {next(model.parameters()).device}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_transcription():
    """测试转录功能（需要一个测试音频文件）"""
    print("\n🔍 测试转录功能...")
    
    # 检查是否有测试音频
    test_audio = "test_audio.wav"
    if not os.path.exists(test_audio):
        print(f"⚠️  未找到测试音频文件: {test_audio}")
        print("💡 跳过转录测试（这是可选的）")
        return True
    
    try:
        import whisper
        
        model = whisper.load_model("base")
        result = model.transcribe(test_audio, language="en")
        
        print(f"✅ 转录成功！")
        print(f"📝 识别文本: {result['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 转录测试失败: {e}")
        return False


def main():
    """主测试流程"""
    print("=" * 60)
    print("🎤 Whisper 语音评分功能 - 安装验证")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 依赖导入
    results.append(("依赖导入", test_imports()))
    
    # 测试 2: FFmpeg
    results.append(("FFmpeg", test_ffmpeg()))
    
    # 测试 3: 模型加载
    results.append(("模型加载", test_whisper_model()))
    
    # 测试 4: 转录功能（可选）
    results.append(("转录功能", test_transcription()))
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12} {status}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！Whisper 已正确安装。")
        print("\n🚀 下一步:")
        print("   1. 启动后端: cd backend && python main.py")
        print("   2. 启动前端: cd frontend && npm run dev")
        print("   3. 访问: http://localhost:5173/ai-create")
        print("   4. 录音并点击'评分'按钮测试功能")
        return 0
    else:
        print("\n⚠️  部分测试失败，请查看上面的错误信息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
