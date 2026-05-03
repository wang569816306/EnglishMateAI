"""
TTS (Text-to-Speech) API 路由
使用 Edge-TTS 提供高质量的文本转语音服务
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt_auth import get_current_user
from pydantic import BaseModel
import base64

router = APIRouter(prefix="/tts", tags=["语音合成"])


class TTSRequest(BaseModel):
    """TTS 请求模型"""
    text: str
    voice: str = "en-US-AriaNeural"  # 默认美式女声
    rate: str = "+0%"  # 语速调整
    pitch: str = "+0Hz"  # 音调调整


# 可用的语音列表
AVAILABLE_VOICES = {
    # 美式英语
    "en-US-AriaNeural": "美式女声 - Aria (温柔清晰，推荐)",
    "en-US-EricNeural": "美式男声 - Eric (沉稳标准)",
    "en-US-JennyNeural": "美式女声 - Jenny (友好自然)",
    "en-US-GuyNeural": "美式男声 - Guy (温暖亲切)",
    
    # 英式英语
    "en-GB-SoniaNeural": "英式女声 - Sonia (优雅 BBC 腔)",
    "en-GB-ThomasNeural": "英式男声 - Thomas (标准英音)",
    "en-GB-RyanNeural": "英式男声 - Ryan (清晰标准)",
}


@router.get("/voices")
async def get_available_voices():
    """
    获取可用的语音列表
    """
    return {
        "code": 200,
        "msg": "成功",
        "data": [
            {"id": vid, "name": vname} 
            for vid, vname in AVAILABLE_VOICES.items()
        ]
    }


@router.post("/synthesize-base64")
async def synthesize_speech_base64(
    request: TTSRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    将文本转换为语音（返回 base64 编码）
    
    适合前端直接使用，不需要处理流式响应
    
    Args:
        request: 包含 text, voice, rate, pitch
        
    Returns:
        base64 编码的音频数据
    """
    try:
        import edge_tts
        
        # 验证语音是否可用
        if request.voice not in AVAILABLE_VOICES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的语音: {request.voice}"
            )
        
        # 验证文本
        if len(request.text) > 1000 or not request.text.strip():
            raise HTTPException(
                status_code=400,
                detail="文本长度不能超过 1000 字符且不能为空"
            )
        
        # 使用 edge-tts 生成音频
        communicate = edge_tts.Communicate(
            text=request.text,
            voice=request.voice,
            rate=request.rate,
            pitch=request.pitch
        )
        
        # 收集音频数据
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        
        # 转换为 base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        return {
            "code": 200,
            "msg": "语音合成成功",
            "data": {
                "audio": audio_base64,
                "format": "mp3",
                "voice": request.voice,
                "text_length": len(request.text)
            }
        }
        
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Edge-TTS 未安装，请运行: pip install edge-tts"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"语音合成失败: {str(e)}"
        )
