from app.core.redis import redis_client
from langchain_core.messages import HumanMessage, AIMessage
import redis as redis_module

MAX_ROUND = 6  # 只保留最近6轮


def _redis_available() -> bool:
    """检查 Redis 是否可用"""
    try:
        redis_client.ping()
        return True
    except (redis_module.ConnectionError, redis_module.TimeoutError, ConnectionRefusedError):
        return False


def get_history(session_id: str):
    """获取记忆，Redis 不可用时返回空历史"""
    if not _redis_available():
        print(f"⚠️ Redis 不可用，无法获取会话历史 [{session_id}]")
        return []
    key = f"english:session:{session_id}"
    history = []
    try:
        messages = redis_client.lrange(key, -MAX_ROUND * 2, -1)
        for idx, msg in enumerate(messages):
            if idx % 2 == 0:
                history.append(HumanMessage(content=msg))
            else:
                history.append(AIMessage(content=msg))
    except (redis_module.ConnectionError, redis_module.TimeoutError, ConnectionRefusedError):
        print(f"⚠️ Redis 连接失败，返回空历史")
    return history


def save_history(session_id: str, user_msg, ai_msg):
    """保存记忆，Redis 不可用时跳过"""
    if not _redis_available():
        return
    key = f"english:session:{session_id}"
    try:
        redis_client.rpush(key, user_msg)
        redis_client.rpush(key, ai_msg)
        redis_client.expire(key, 7 * 24 * 3600)
    except (redis_module.ConnectionError, redis_module.TimeoutError, ConnectionRefusedError):
        pass


def clear_chat_history(session_id: str):
    """清空记忆"""
    if not _redis_available():
        return
    key = f"english_ai:chat_history:{session_id}"
    try:
        redis_client.delete(key)
    except (redis_module.ConnectionError, redis_module.TimeoutError, ConnectionRefusedError):
        pass
