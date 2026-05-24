from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from app.settings import settings
from app.core.logging import logger
from app.core.prompt_loader import load_prompt
from app.core.memory import get_history, save_history
from app.core.rag import get_rag_context
from app.agents.tools import AVAILABLE_TOOLS, TOOLS_DESCRIPTION
from sqlalchemy.orm import Session
from app.models.user import Message as MessageModel
import json

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

# ==================== Tool Calling 流式 Agent ====================

# 初始化支持 Tool Calling 的 LLM
llm_with_tools = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.TEMPERATURE,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    streaming=True,
)

# 构建增强版 Prompt（包含工具描述）
enhanced_system_prompt = f"""{system_prompt}

{TOOLS_DESCRIPTION}

重要规则：
1. 当用户的问题可以通过工具更好地回答时，优先调用工具
2. 调用工具后，基于工具返回的结果用自然语言回答用户
3. 如果工具调用失败，尝试用自己的知识回答或告知用户失败原因
4. 不要向用户暴露你使用了工具，就像这是你自己的知识一样
"""

# 创建 Prompt 模板（支持 Agent）
prompt_with_tools = ChatPromptTemplate.from_messages([
    ("system", enhanced_system_prompt),
    MessagesPlaceholder(variable_name="history"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Agent 执行轨迹
    ("user", "{question}")
])

# 绑定工具到 LLM
llm_bound_tools = llm_with_tools.bind_tools(AVAILABLE_TOOLS)

# 创建 Agent
agent_with_tools = create_tool_calling_agent(llm_bound_tools, AVAILABLE_TOOLS, prompt_with_tools)

# 创建 Agent Executor
agent_executor_with_tools = AgentExecutor(
    agent=agent_with_tools,
    tools=AVAILABLE_TOOLS,
    verbose=False,  # 关闭详细日志，避免干扰流式输出
    max_iterations=3,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)

# 生成推荐问题的函数
async def generate_suggested_questions(user_question: str, ai_response: str) -> list:
    """
    基于AI的回答内容，生成2个相关的推荐问题
    
    Args:
        user_question: 用户的问题
        ai_response: AI的回答
    
    Returns:
        推荐问题列表（最多2个）
    """
    try:
        # 创建一个专门用于生成推荐问题的prompt
        suggestion_prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个英语学习助手。请基于刚才的对话内容，生成2个相关的、用户可能感兴趣的后续问题。
要求：
1. 问题必须与刚才的对话内容相关
2. 问题要具体、有深度，能引导用户继续学习
3. 使用中文提问
4. 每个问题不超过30个字
5. 只返回JSON格式的列表，不要其他内容

示例格式：["问题1", "问题2"]"""),
            ("user", f"""刚才的对话内容：
用户问题：{user_question}
AI回答：{ai_response[:500]}...

请生成2个相关的推荐问题：""")
        ])
        
        suggestion_chain = suggestion_prompt | llm
        
        response = await suggestion_chain.ainvoke({})
        
        # 解析JSON响应
        content = response.content.strip()
        # 移除可能的markdown代码块标记
        if content.startswith('```'):
            content = content.split('\n', 1)[1].rsplit('\n', 1)[0]
        
        questions = json.loads(content)
        
        # 确保返回的是列表且最多2个
        if isinstance(questions, list):
            return questions[:2]
        
        return []
    except Exception as e:
        logger.error(f"生成推荐问题异常: {str(e)}")
        return []

# 流式生成器
async def chat_agent_stream(question: str, session_id: str = "default", db: Session = None, db_session_id: int = None):
    """
    流式聊天Agent（支持RAG和多轮记忆）
    
    Args:
        question: 用户问题
        session_id: 会话ID
        db: 数据库会话
        db_session_id: 数据库中的会话ID
    
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
                # 返回 SSE 格式数据
                yield f"data: {chunk.content}\n\n"
        
        # 保存对话历史到Redis
        save_history(session_id, question, full_response)
        
        # 保存AI回复到数据库
        if db and db_session_id:
            try:
                ai_message = MessageModel(
                    session_id=db_session_id,
                    role="assistant",
                    content=full_response
                )
                db.add(ai_message)
                db.commit()
                logger.info("AI消息已保存到数据库")
            except Exception as e:
                logger.error(f"保存AI消息到数据库失败: {str(e)}")
                db.rollback()
        
        logger.info("流式聊天请求处理完成")
        
        # 生成推荐问题（基于AI的回答内容）
        try:
            suggested_questions = await generate_suggested_questions(question, full_response)
            if suggested_questions:
                # 发送推荐问题
                yield f"data: [SUGGESTED_QUESTIONS]{json.dumps(suggested_questions, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"生成推荐问题失败: {str(e)}")
        
        # 发送完成信号
        yield "data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"流式聊天请求处理失败: {str(e)}")
        # 以 SSE 格式返回错误信息，避免客户端无响应
        yield f"data: [ERROR]{str(e)}\n\n"
        yield "data: [DONE]\n\n"


# ==================== 支持 Tool Calling 的流式 Agent ====================

async def chat_agent_stream_with_tools(question: str, session_id: str = "default", db: Session = None, db_session_id: int = None):
    """
    流式聊天Agent（支持 Tool Calling、RAG和多轮记忆）
    
    注意：由于 LangChain 的 Agent Executor 不支持真正的流式工具调用，
    我们采用“先执行工具，再流式输出”的策略。
    
    Args:
        question: 用户问题
        session_id: 会话ID
        db: 数据库会话
        db_session_id: 数据库中的会话ID
    
    Yields:
        流式文本片段（SSE 格式）
    """
    try:
        logger.info(f"收到流式 Tool Calling 请求 [session:{session_id}]: {question[:50]}...")
        
        # 1. 获取历史对话
        history = get_history(session_id)
        
        # 2. RAG检索相关知识
        context = get_rag_context(question)
        
        # 3. 调用 Agent Executor（非流式，会等待工具调用完成）
        response = await agent_executor_with_tools.ainvoke({
            "question": question,
            "history": history,
            "context": context
        })
        
        full_response = response.get("output", "")
        
        # 4. 流式输出回答（模拟流式效果，逐字符发送）
        for char in full_response:
            yield f"data: {char}\n\n"
        
        # 5. 保存对话历史到Redis
        save_history(session_id, question, full_response)
        
        # 6. 保存AI回复到数据库
        if db and db_session_id:
            try:
                ai_message = MessageModel(
                    session_id=db_session_id,
                    role="assistant",
                    content=full_response
                )
                db.add(ai_message)
                db.commit()
                logger.info("AI消息已保存到数据库")
            except Exception as e:
                logger.error(f"保存AI消息到数据库失败: {str(e)}")
                db.rollback()
        
        logger.info("流式 Tool Calling 聊天请求处理完成")
        
        # 7. 生成推荐问题
        try:
            suggested_questions = await generate_suggested_questions(question, full_response)
            if suggested_questions:
                yield f"data: [SUGGESTED_QUESTIONS]{json.dumps(suggested_questions, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"生成推荐问题失败: {str(e)}")
        
        # 8. 发送完成信号
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"流式 Tool Calling 请求处理失败: {str(e)}")
        # 降级方案：使用普通流式 Agent
        logger.info("降级到普通流式模式...")
        async for chunk in chat_agent_stream(question, session_id, db, db_session_id):
            yield chunk
