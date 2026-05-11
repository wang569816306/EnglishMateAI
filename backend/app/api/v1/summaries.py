from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import logging
from app.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端（兼容通义千问）
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


class SummarizeRequest(BaseModel):
    video_title: str
    subtitles: str
    language: str = "zh"


async def generate_summary_sse(title: str, subtitles: str, language: str = "zh"):
    """使用通义千问生成流式总结"""
    try:
        # SSE 格式输出
        yield "event: summary\n"
        yield f"data: {json.dumps({'status': 'started', 'message': '开始生成总结...'}, ensure_ascii=False)}\n\n"

        # 构建提示词
        prompt = f"""你是一个专业的视频内容分析助手。请根据以下视频标题和字幕内容，生成详细的视频总结。

视频标题：{title}
字幕内容：{subtitles}

请按照以下格式输出：
# 视频概述
（简要介绍视频的主要内容和目的）

## 内容大纲
1. 核心主题介绍
   - 主要讨论点
   - 关键概念说明

2. 重要内容分析
   - 详细的内容解析
   - 关键要点总结

3. 结论与总结
   - 主要观点和结论
   - 建议的后续行动
"""

        # 调用通义千问 API（流式）
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的视频内容分析助手，擅长提取视频核心内容并生成结构化总结。"},
                {"role": "user", "content": prompt}
            ],
            stream=True,
            temperature=0.7
        )

        # 流式输出 AI 回复
        full_content = ""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    content = delta.content
                    full_content += content
                    yield f"data: {json.dumps({'type': 'chunk', 'content': content}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'status': 'completed', 'message': '总结完成'}, ensure_ascii=False)}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"


@router.post("/summarize")
async def summarize_video(request: SummarizeRequest):
    """视频总结流式输出"""
    return StreamingResponse(
        generate_summary_sse(request.video_title, request.subtitles, request.language),
        media_type="text/event-stream"
    )


class QuestionRequest(BaseModel):
    """问答请求"""
    video_title: str
    subtitles: str
    question: str
    language: str = "zh"


@router.post("/ask-question")
async def ask_question(request: QuestionRequest):
    """AI 视频内容问答"""
    try:
        # 构建提示词
        prompt = f"""你是一个专业的视频内容分析助手。基于以下视频内容，回答用户的问题。

视频标题：{request.video_title}
字幕内容：{request.subtitles[:2000]}  # 限制长度避免超出token限制

用户问题：{request.question}

请根据视频内容提供准确、详细的回答。如果问题与视频内容无关，请礼貌地说明。"""

        # 调用通义千问 API
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个专业的视频内容分析助手，擅长根据视频内容回答用户问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        answer = response.choices[0].message.content
        
        return {
            "code": 200,
            "message": "成功",
            "data": {
                "answer": answer
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")
