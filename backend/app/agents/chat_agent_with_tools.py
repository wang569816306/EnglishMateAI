"""
支持 Tool Calling 的 AI Agent
在不改变原有功能的基础上，增加工具调用能力
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from app.settings import settings
from app.core.logging import logger
from app.core.exceptions import APIException
from app.core.prompt_loader import load_prompt
from app.core.memory import get_history, save_history
from app.core.rag import get_rag_context
from app.agents.tools import AVAILABLE_TOOLS, TOOLS_DESCRIPTION


# 初始化 LLM（需要支持 function calling 的模型）
llm = ChatOpenAI(
    model=settings.OPENAI_MODEL,
    temperature=settings.TEMPERATURE,
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

# 加载系统提示词
system_prompt = load_prompt("english_teacher")

# 构建增强版 Prompt（包含工具描述）
enhanced_system_prompt = f"""{system_prompt}

{TOOLS_DESCRIPTION}

重要规则：
1. 当用户的问题可以通过工具更好地回答时，优先调用工具
2. 调用工具后，基于工具返回的结果用自然语言回答用户
3. 如果工具调用失败，尝试用自己的知识回答或告知用户失败原因
4. 不要向用户暴露你使用了工具，就像这是你自己的知识一样
"""

# 创建 Prompt 模板
prompt = ChatPromptTemplate.from_messages([
    ("system", enhanced_system_prompt),
    MessagesPlaceholder(variable_name="history"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # Agent 执行轨迹
    ("user", "{question}")
])

# 绑定工具到 LLM
llm_with_tools = llm.bind_tools(AVAILABLE_TOOLS)

# 创建 Agent
agent = create_tool_calling_agent(llm_with_tools, AVAILABLE_TOOLS, prompt)

# 创建 Agent Executor（带错误处理和最大迭代次数）
agent_executor = AgentExecutor(
    agent=agent,
    tools=AVAILABLE_TOOLS,
    verbose=True,  # 调试模式，打印工具调用过程
    max_iterations=3,  # 最多调用3次工具，防止无限循环
    handle_parsing_errors=True,  # 处理解析错误
    return_intermediate_steps=False  # 不返回中间步骤
)


async def chat_agent_with_tools(question: str, session_id: str = "default") -> str:
    """
    支持 Tool Calling 的聊天 Agent
    
    Args:
        question: 用户问题
        session_id: 会话ID
        
    Returns:
        AI 回答内容
        
    Raises:
        APIException: 当 AI 服务异常时抛出
    """
    try:
        logger.info(f"收到 Tool Calling 聊天请求 [session:{session_id}]: {question[:50]}...")
        
        # 1. 获取历史对话
        history = get_history(session_id)
        
        # 2. RAG 检索相关知识（作为背景信息）
        context = get_rag_context(question)
        
        # 3. 调用 Agent Executor
        response = await agent_executor.ainvoke({
            "question": question,
            "history": history,
            "context": context
        })
        
        # 4. 提取回答内容
        ai_content = response.get("output", "")
        
        # 5. 保存对话历史
        save_history(session_id, question, ai_content)
        
        logger.info(f"Tool Calling 聊天请求处理成功 [session:{session_id}]")
        return ai_content
        
    except Exception as e:
        logger.error(f"Tool Calling 聊天请求处理失败: {str(e)}")
        # 降级方案：如果 Tool Calling 失败，使用原始 Agent
        logger.info("降级到普通聊天模式...")
        from app.agents.chat_agent import chat_agent
        return await chat_agent(question, session_id)


# 流式版本（暂时不支持流式工具调用，后续可扩展）
async def chat_agent_stream_with_tools(question: str, session_id: str = "default"):
    """
    流式聊天 Agent（带 Tool Calling）
    注意：目前工具调用不支持流式，会先执行工具再流式输出
    
    Yields:
        流式文本片段
    """
    try:
        logger.info(f"收到流式 Tool Calling 请求 [session:{session_id}]: {question[:50]}...")
        
        # 先执行工具调用获取完整回答
        full_response = await chat_agent_with_tools(question, session_id)
        
        # 然后流式输出（模拟流式效果）
        for char in full_response:
            yield f"data: {char}\n\n"
            
    except Exception as e:
        logger.error(f"流式 Tool Calling 失败: {str(e)}")
        yield f"data: [错误: {str(e)}]\n\n"
