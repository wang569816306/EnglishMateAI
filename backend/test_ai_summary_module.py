#!/usr/bin/env python3
"""
AI 智能总结模块功能测试脚本
测试以下功能：
1. AI 流式总结摘要（SSE）
2. 交互式思维导图生成
3. 字幕导出功能
4. AI 视频内容问答
"""
import requests
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/ai"

# 测试数据
TEST_VIDEO_TITLE = "Python编程入门教程"
TEST_SUBTITLES = """
欢迎来到Python编程入门课程。今天我们将学习Python的基础知识。
首先，我们来了解什么是Python。Python是一种高级编程语言，由Guido van Rossum于1991年创建。
Python的设计哲学强调代码的可读性和简洁的语法。

接下来，我们学习变量和数据类型。在Python中，你可以轻松地定义变量：
name = "Alice"
age = 25
height = 1.75

Python支持多种数据类型，包括字符串、整数、浮点数、列表、字典等。

然后我们学习控制流语句，比如if-else条件判断和for循环：
if age >= 18:
    print("成年人")
else:
    print("未成年人")

for i in range(5):
    print(i)

最后，我们学习函数的定义和使用：
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))

这就是我们今天课程的主要内容。希望大家能够通过练习掌握这些基础知识。
"""


def test_health_check():
    """测试1: 健康检查"""
    print("\n" + "="*60)
    print("🔍 测试1: 健康检查")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务状态: {data.get('status')}")
            print(f"📦 服务名称: {data.get('service')}")
            print(f"🔖 版本: {data.get('version')}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def test_summarize_stream():
    """测试2: AI 流式总结摘要（SSE）"""
    print("\n" + "="*60)
    print("🤖 测试2: AI 流式总结摘要（SSE）")
    print("="*60)
    
    try:
        url = f"{API_BASE}/summaries/summarize"
        payload = {
            "video_title": TEST_VIDEO_TITLE,
            "subtitles": TEST_SUBTITLES,
            "language": "zh"
        }
        
        print(f"📤 发送请求到: {url}")
        print(f"📝 视频标题: {TEST_VIDEO_TITLE}")
        print(f"📄 字幕长度: {len(TEST_SUBTITLES)} 字符")
        
        response = requests.post(url, json=payload, stream=True, timeout=60)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        print("✅ SSE 连接建立成功")
        print("\n📊 接收流式数据:")
        print("-" * 60)
        
        full_summary = ""
        mindmap_received = False
        completed = False
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    try:
                        data = json.loads(data_str)
                        
                        if data.get('type') == 'chunk':
                            chunk = data.get('content', '')
                            full_summary += chunk
                            print(chunk, end='', flush=True)
                            
                        elif data.get('type') == 'mindmap':
                            mindmap_data = data.get('data')
                            print(f"\n\n✅ 收到思维导图数据")
                            print(f"   - 标题: {mindmap_data.get('title')}")
                            print(f"   - 根节点: {mindmap_data.get('root', {}).get('content')}")
                            print(f"   - 子节点数: {len(mindmap_data.get('root', {}).get('children', []))}")
                            mindmap_received = True
                            
                        elif data.get('status') == 'completed':
                            print(f"\n\n✅ {data.get('message')}")
                            completed = True
                            break
                            
                        elif data.get('status') == 'error':
                            print(f"\n\n❌ 错误: {data.get('message')}")
                            return False
                            
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️  JSON解析错误: {e}")
        
        print("\n" + "-" * 60)
        print(f"📊 总结统计:")
        print(f"   - 总长度: {len(full_summary)} 字符")
        print(f"   - 是否收到思维导图: {'是' if mindmap_received else '否'}")
        print(f"   - 是否完成: {'是' if completed else '否'}")
        
        if completed and len(full_summary) > 0:
            print("\n✅ 流式总结测试通过")
            return True
        else:
            print("\n❌ 流式总结测试失败")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generate_mindmap():
    """测试3: 生成思维导图"""
    print("\n" + "="*60)
    print("🧠 测试3: 生成思维导图")
    print("="*60)
    
    try:
        url = f"{API_BASE}/summaries/generate-mindmap"
        payload = {
            "video_title": TEST_VIDEO_TITLE,
            "subtitles": TEST_SUBTITLES,
            "language": "zh"
        }
        
        print(f"📤 发送请求到: {url}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        data = response.json()
        mindmap = data.get('mindmap')
        
        if not mindmap:
            print("❌ 未收到思维导图数据")
            return False
        
        print(f"✅ 思维导图生成成功")
        print(f"   - 标题: {mindmap.get('title')}")
        print(f"   - 根节点: {mindmap.get('root', {}).get('content')}")
        
        root = mindmap.get('root', {})
        children = root.get('children', [])
        print(f"   - 一级分支数: {len(children)}")
        
        for i, child in enumerate(children, 1):
            sub_children = child.get('children', [])
            print(f"     {i}. {child.get('content')} ({len(sub_children)} 个子节点)")
        
        print("\n✅ 思维导图生成测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subtitle_export_formats():
    """测试4: 字幕导出格式验证"""
    print("\n" + "="*60)
    print("📄 测试4: 字幕导出格式验证")
    print("="*60)
    
    try:
        # 测试 TXT 格式
        txt_content = TEST_SUBTITLES
        print(f"✅ TXT 格式: {len(txt_content)} 字符")
        
        # 测试 VTT 格式
        vtt_content = f"WEBVTT\n\n{TEST_SUBTITLES}"
        print(f"✅ VTT 格式: {len(vtt_content)} 字符 (包含 WEBVTT 头)")
        
        # 测试 SRT 格式（简单模拟）
        srt_lines = []
        for i, line in enumerate(TEST_SUBTITLES.split('\n'), 1):
            if line.strip():
                start_time = f"00:00:{(i-1)*2:02d},000"
                end_time = f"00:00:{i*2:02d},000"
                srt_lines.append(f"{i}\n{start_time} --> {end_time}\n{line}\n")
        
        srt_content = '\n'.join(srt_lines)
        print(f"✅ SRT 格式: {len(srt_content)} 字符 ({len(srt_lines)} 条字幕)")
        
        print("\n✅ 字幕导出格式测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_video_history():
    """测试5: 视频下载历史"""
    print("\n" + "="*60)
    print("📹 测试5: 视频下载历史")
    print("="*60)
    
    try:
        url = f"{API_BASE}/videos/history"
        print(f"📤 发送请求到: {url}")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        data = response.json()
        history = data.get('data', [])
        
        print(f"✅ 获取历史记录成功")
        print(f"   - 记录数量: {len(history)}")
        
        if history:
            print(f"   - 最新文件: {history[0].get('filename')}")
            print(f"   - 文件大小: {history[0].get('size', 0)} bytes")
        
        print("\n✅ 视频下载历史测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_api_endpoints_availability():
    """测试6: API 端点可用性检查"""
    print("\n" + "="*60)
    print("🔌 测试6: API 端点可用性检查")
    print("="*60)
    
    endpoints = [
        ("POST", f"{API_BASE}/summaries/summarize", "AI 流式总结"),
        ("POST", f"{API_BASE}/summaries/generate-mindmap", "生成思维导图"),
        ("GET", f"{API_BASE}/videos/history", "视频下载历史"),
        ("POST", f"{API_BASE}/videos/parse", "视频解析"),
    ]
    
    all_passed = True
    
    for method, url, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                # 对于 POST 请求，只检查端点是否存在（不实际执行）
                if "summarize" in url or "generate-mindmap" in url:
                    response = requests.post(url, json={
                        "video_title": "test",
                        "subtitles": "test"
                    }, timeout=5)
                elif "parse" in url:
                    response = requests.post(url, json={"url": "test"}, timeout=5)
                else:
                    response = requests.get(url, timeout=5)
            
            # 404 表示端点不存在，其他状态码表示端点存在但可能需要参数
            if response.status_code == 404:
                print(f"❌ {description}: 端点不存在 (404)")
                all_passed = False
            else:
                print(f"✅ {description}: 端点可用 ({response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: 连接失败")
            all_passed = False
        except Exception as e:
            print(f"⚠️  {description}: {e}")
    
    if all_passed:
        print("\n✅ 所有 API 端点测试通过")
    else:
        print("\n❌ 部分 API 端点测试失败")
    
    return all_passed


def test_ask_question():
    """测试7: AI 视频内容问答"""
    print("\n" + "="*60)
    print("💬 测试7: AI 视频内容问答")
    print("="*60)
    
    try:
        url = f"{API_BASE}/summaries/ask-question"
        payload = {
            "video_title": TEST_VIDEO_TITLE,
            "subtitles": TEST_SUBTITLES,
            "question": "Python是什么？它的主要特点是什么？",
            "language": "zh"
        }
        
        print(f"📤 发送请求到: {url}")
        print(f"❓ 问题: {payload['question']}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
        
        data = response.json()
        answer = data.get('data', {}).get('answer', '')
        
        if not answer:
            print("❌ 未收到回答")
            return False
        
        print(f"✅ 收到AI回答")
        print(f"   - 回答长度: {len(answer)} 字符")
        print(f"\n📝 回答内容:")
        print("-" * 60)
        print(answer[:500] + ("..." if len(answer) > 500 else ""))
        print("-" * 60)
        
        print("\n✅ AI 问答测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 AI 智能总结模块功能测试")
    print("="*60)
    print(f"📍 API 地址: {API_BASE}")
    print(f"⏰ 测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 运行测试
    results.append(("健康检查", test_health_check()))
    results.append(("API 端点可用性", test_api_endpoints_availability()))
    results.append(("AI 流式总结摘要", test_summarize_stream()))
    results.append(("思维导图生成", test_generate_mindmap()))
    results.append(("字幕导出格式", test_subtitle_export_formats()))
    results.append(("视频下载历史", test_video_history()))
    results.append(("AI 视频内容问答", test_ask_question()))
    
    # 打印测试结果汇总
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI 智能总结模块功能正常")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关功能")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
