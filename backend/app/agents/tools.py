"""
AI Agent 工具定义
提供可供 LLM 调用的工具函数
"""
from langchain.tools import tool
from typing import Optional
import requests
from app.services.video_downloader import VideoDownloader
from app.services.download_manager import download_manager


# 初始化视频下载器
video_downloader = VideoDownloader()


@tool
def search_english_dictionary(word: str) -> dict:
    """
    查询英语单词的详细信息，包括释义、音标、例句等。
    当用户询问单词含义、发音、用法时使用此工具。
    
    Args:
        word: 要查询的英语单词
        
    Returns:
        包含单词详细信息的字典
    """
    try:
        # 使用免费词典 API
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()[0]
            
            result = {
                "word": data.get("word", word),
                "phonetic": data.get("phonetic", ""),
                "meanings": []
            }
            
            # 提取释义和例句
            for meaning in data.get("meanings", [])[:2]:  # 只取前2个词性
                meaning_info = {
                    "part_of_speech": meaning.get("partOfSpeech", ""),
                    "definitions": []
                }
                
                for definition in meaning.get("definitions", [])[:2]:  # 每个词性只取2个释义
                    def_info = {
                        "definition": definition.get("definition", ""),
                        "example": definition.get("example", "")
                    }
                    meaning_info["definitions"].append(def_info)
                
                result["meanings"].append(meaning_info)
            
            return result
        else:
            return {"error": f"未找到单词 '{word}' 的信息"}
            
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}


@tool
def calculate_math(expression: str) -> dict:
    """
    执行数学计算。当用户需要进行数学运算时使用此工具。
    
    Args:
        expression: 数学表达式，如 "30 * 365", "100 / 7" 等
        
    Returns:
        计算结果
    """
    try:
        # 安全评估数学表达式（只允许数字和运算符）
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return {"error": "表达式包含非法字符"}
        
        result = eval(expression)
        return {
            "expression": expression,
            "result": result
        }
    except Exception as e:
        return {"error": f"计算失败: {str(e)}"}


@tool
def get_video_info(url: str) -> dict:
    """
    解析视频链接，获取视频信息（标题、时长、上传者等）。
    当用户提供视频链接并询问相关信息时使用此工具。
    支持 B站、YouTube、抖音等 1800+ 平台。
    
    Args:
        url: 视频链接
        
    Returns:
        视频信息字典
    """
    try:
        video_info = video_downloader.parse_video(url)
        
        return {
            "title": video_info.get("title", ""),
            "duration": video_info.get("duration_string", ""),
            "uploader": video_info.get("uploader", ""),
            "platform": video_info.get("platform", ""),
            "view_count": video_info.get("view_count", 0),
            "description": video_info.get("description", "")[:200],
            "has_subtitles": len(video_info.get("subtitles", [])) > 0,
            "subtitle_languages": video_info.get("subtitles", [])[:5]
        }
    except Exception as e:
        return {"error": f"视频解析失败: {str(e)}"}


@tool
def get_storage_stats() -> dict:
    """
    获取服务器下载目录的存储统计信息。
    当用户询问存储空间使用情况时使用此工具。
    
    Returns:
        存储统计信息
    """
    try:
        stats = download_manager.get_storage_stats()
        return {
            "total_size_mb": round(stats["total_size_mb"], 2),
            "max_size_gb": stats["max_size_gb"],
            "usage_percent": round(stats["usage_percent"], 2),
            "file_count": stats["file_count"],
            "expire_hours": stats["expire_hours"]
        }
    except Exception as e:
        return {"error": f"获取存储统计失败: {str(e)}"}


# 工具列表 - 供 Agent 使用
AVAILABLE_TOOLS = [
    search_english_dictionary,
    calculate_math,
    get_video_info,
    get_storage_stats,
]

# 工具描述 - 用于 Prompt
TOOLS_DESCRIPTION = """
你可以使用以下工具来帮助用户：

1. search_english_dictionary: 查询英语单词的释义、音标、例句
   - 使用场景：用户询问单词含义、发音、用法
   - 示例："serendipity 是什么意思？"

2. calculate_math: 执行数学计算
   - 使用场景：用户需要进行数学运算
   - 示例："如果每天学30个单词，一年能学多少个？"

3. get_video_info: 解析视频链接获取信息
   - 使用场景：用户提供视频链接并询问相关信息
   - 示例："帮我看看这个视频：https://bilibili.com/xxx"

4. get_storage_stats: 获取服务器存储统计
   - 使用场景：用户询问存储空间使用情况
   - 示例："服务器还剩多少空间？"

使用工具时，请确保参数准确，并在获得结果后用自然语言回答用户。
"""
