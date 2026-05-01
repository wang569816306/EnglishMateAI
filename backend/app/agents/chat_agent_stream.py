from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.settings import settings
from app.core.logging import logger
from app.core.prompt_loader import load_prompt
from app.core.memory import get_history, save_history
from app.core.rag import get_rag_context

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.TEMPERATURE,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    streaming=True,
)

system_prompt = load_prompt("english_teacher")
prompt = ChatPromptTemplate.from_messages([
    ("system", f"{system_prompt}\n\n以下是相关知识库资料，请优先基于这些资料回答问题：\n{{context}}"),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{question}")
])

chain = prompt | llm

# 流式生成器
async def chat_agent_stream(question: str, session_id: str = "default"):
    """
    流式聊天Agent（支持RAG和多轮记忆）
    
    Args:
        question: 用户问题
        session_id: 会话ID
    
    Yields:
        流式文本片段
    """
    try:
        logger.info(f"收到流式聊天请求 [session:{session_id}]: {question[:50]}...")
        
        # 1. 获取历史对话
        history = get_history(session_id)
        
        # 2. RAG检索相关知识
        context = get_rag_context(question)
        print("流式-RAG检索结果-----------------", context)
        
        full_response = ""
        async for chunk in chain.astream({
            "question": question,
            "history": history,
            "context": context
        }):
            if chunk.content:
                full_response += chunk.content
                yield chunk.content
        
        # 3. 保存对话历史
        save_history(session_id, question, full_response)
        
        logger.info("流式聊天请求处理完成")
    except Exception as e:
        logger.error(f"流式聊天请求处理失败: {str(e)}")
        raise