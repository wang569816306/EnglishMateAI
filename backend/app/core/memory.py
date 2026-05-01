from app.core.redis import redis_client
from langchain_core.messages import HumanMessage, AIMessage

MAX_ROUND = 6  # 只保留最近6轮


def get_history(session_id: str):
    """获取记忆"""
    key = f"english:session:{session_id}"
    history = []
    messages = redis_client.lrange(key, -MAX_ROUND * 2, -1)
    for idx, msg in enumerate(messages):
        if idx % 2 == 0:
            history.append(HumanMessage(content=msg))
        else:
            history.append(AIMessage(content=msg))
    return history


def save_history(session_id: str, user_msg, ai_msg):
    """保存记忆"""
    key = f"english:session:{session_id}"
    redis_client.rpush(key, user_msg)
    redis_client.rpush(key, ai_msg)
    redis_client.expire(key, 7 * 24 * 3600)


def clear_chat_history(session_id: str):
    """清空记忆"""
    key = f"english_ai:chat_history:{session_id}"
    redis_client.delete(key)
