"""
语音评分 API
使用 Whisper 进行语音识别，并与原文对比给出评分
"""
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional
import tempfile
import os
import re
from difflib import SequenceMatcher
from app.auth.jwt_auth import get_current_user

router = APIRouter()


def calculate_word_similarity(original: str, recognized: str) -> dict:
    """
    计算原文和识别文本的相似度，返回逐词评分
    
    Args:
        original: 原始文本
        recognized: 识别文本
    
    Returns:
        包含评分信息的字典
    """
    # 清理文本（去除标点，转小写）
    def clean_text(text):
        # 保留字母、空格和连字符
        text = re.sub(r"[^a-zA-Z\s'-]", "", text.lower())
        return text.split()
    
    original_words = clean_text(original)
    recognized_words = clean_text(recognized)
    
    # 使用序列匹配器找出差异
    matcher = SequenceMatcher(None, original_words, recognized_words)
    
    word_scores = []
    correct_count = 0
    total_words = len(original_words)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # 完全匹配的单词
            for idx in range(i1, i2):
                word_scores.append({
                    'word': original_words[idx],
                    'score': 100,
                    'status': 'correct'
                })
                correct_count += 1
        elif tag == 'replace':
            # 替换的单词（读错）
            for idx in range(i1, i2):
                word_scores.append({
                    'word': original_words[idx] if idx < len(original_words) else '',
                    'recognized': recognized_words[j1] if j1 < len(recognized_words) else '',
                    'score': 30,
                    'status': 'wrong'
                })
            j1 += (i2 - i1)
        elif tag == 'delete':
            # 删除的单词（漏读）
            for idx in range(i1, i2):
                word_scores.append({
                    'word': original_words[idx],
                    'score': 0,
                    'status': 'missing'
                })
        elif tag == 'insert':
            # 插入的单词（多读）
            for idx in range(j1, j2):
                word_scores.append({
                    'word': recognized_words[idx],
                    'score': 50,
                    'status': 'extra'
                })
    
    # 计算总体评分
    accuracy_score = (correct_count / total_words * 100) if total_words > 0 else 0
    
    # 流利度评分（基于是否有停顿、重复等）
    fluency_score = min(100, accuracy_score + 10)  # 简化计算
    
    # 完整度评分（是否读完所有单词）
    completeness_score = (len([w for w in word_scores if w['status'] in ['correct', 'wrong']]) / total_words * 100) if total_words > 0 else 0
    
    return {
        'overall_score': round((accuracy_score * 0.5 + fluency_score * 0.3 + completeness_score * 0.2), 1),
        'accuracy': round(accuracy_score, 1),
        'fluency': round(fluency_score, 1),
        'completeness': round(completeness_score, 1),
        'word_details': word_scores,
        'recognized_text': ' '.join(recognized_words),
        'original_text': ' '.join(original_words)
    }


@router.post("/evaluate-pronunciation")
async def evaluate_pronunciation(
    file: UploadFile = File(...),
    original_text: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    评估发音准确度
    
    Args:
        file: 录音文件（webm/mp3/wav）
        original_text: 原始文本
    
    Returns:
        评分结果，包括总分和逐词评分
    """
    try:
        import whisper
        
        # 保存上传的文件到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # 加载 Whisper 模型（使用 base 模型，平衡速度和准确度）
            # 首次加载会下载模型，之后会使用缓存
            model = whisper.load_model("base")
            
            # 转录音频
            result = model.transcribe(
                tmp_file_path,
                language="en",
                task="transcribe"
            )
            
            recognized_text = result.get("text", "").strip()
            
            if not recognized_text:
                raise HTTPException(status_code=400, detail="未能识别出语音内容")
            
            # 计算评分
            evaluation = calculate_word_similarity(original_text, recognized_text)
            
            return {
                "code": 200,
                "msg": "评分完成",
                "data": evaluation
            }
        
        finally:
            # 删除临时文件
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Whisper 未安装，请运行: pip install openai-whisper"
        )
    except Exception as e:
        print(f"❌ 评分失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"评分失败: {str(e)}")


@router.get("/available-models")
async def get_available_models():
    """
    获取可用的 Whisper 模型列表
    """
    models = [
        {"name": "tiny", "size": "75MB", "speed": "最快", "accuracy": "较低"},
        {"name": "base", "size": "150MB", "speed": "快", "accuracy": "中等"},
        {"name": "small", "size": "500MB", "speed": "中等", "accuracy": "较高"},
        {"name": "medium", "size": "1.5GB", "speed": "慢", "accuracy": "高"},
        {"name": "large", "size": "3GB", "speed": "最慢", "accuracy": "最高"}
    ]
    
    return {
        "code": 200,
        "msg": "成功",
        "data": {
            "models": models,
            "current": "base",
            "note": "首次使用会自动下载模型，之后会缓存到本地"
        }
    }
