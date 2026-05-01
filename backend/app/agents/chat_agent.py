from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.settings import settings
from app.core.logging import logger
from app.core.exceptions import APIException
from app.core.prompt_loader import load_prompt
from app.core.memory import get_history, save_history  # 多轮记忆
from app.core.rag import get_rag_context

# 初始化 LLM
llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.TEMPERATURE,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

system_prompt = load_prompt("english_teacher")
print('------------system_prompt', system_prompt)
# 提示词模板
prompt = ChatPromptTemplate.from_messages([
    ("system", f"{system_prompt}\n\n以下是相关知识库资料，请优先基于这些资料回答问题：\n{{context}}"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{question}")
])

# 调用链
chain = prompt | llm


# 封装服务函数
async def chat_agent(question: str, session_id: str) -> str:
    """
     带多轮记忆的英语老师聊天Agent

    Args:
        session_id: 用户会话ID（必须）
        question: 用户问题
    
    Returns:
        AI回答内容
    
    Raises:
        APIException: 当AI服务异常时抛出
    """
    try:

        logger.info(f"收到聊天请求: {question[:50]}...")
        # 1. 获取该用户的历史对话 ✅
        history = get_history(session_id)
        context = get_rag_context(question)  # <--- RAG 获取资料
        print("历史记忆-----------------", history)
        print("RAG检索结果-----------------", context)
        response = await chain.ainvoke({
            "question": question,
            "history": history,
            "context": context  # <--- 传入AI
        })

        ai_content = response.content

        # 3. 保存本轮对话到 Redis ✅
        save_history(session_id, question, ai_content)

        logger.info("聊天请求处理成功")
        return ai_content
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        raise APIException(code=500, msg=f"AI服务异常: {str(e)}")
