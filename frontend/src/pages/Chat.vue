<template>
  <div class="chat-container">
    <!-- 欢迎页面 -->
    <div v-if="isWelcomePage" class="welcome-page">
      <div class="welcome-content">
        <h1 class="welcome-title">有什么我能帮你的吗？</h1>
        <div class="suggested-questions">
          <div class="question-chip" v-for="(question, index) in suggestedQuestions" :key="index" @click="handleSuggestedQuestion(question)">
            {{ question }}
          </div>
        </div>
      </div>
    </div>
    
    <!-- 对话消息列表 -->
    <div v-else class="chat-messages" ref="messagesContainer">
      <div class="message-wrapper" v-for="(msg, index) in messages" :key="index">
        <!-- 用户消息 -->
        <div v-if="msg.isUser" class="message-item user-message">
          <div class="message-content">{{ msg.content }}</div>
        </div>
        
        <!-- AI消息 -->
        <div v-else class="message-item ai-message">
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            
            <!-- 推荐问题 -->
            <div v-if="msg.suggestedQuestions && msg.suggestedQuestions.length > 0" class="suggested-questions-inline">
              <div class="suggested-label">相关提问：</div>
              <div class="suggested-question-item" 
                   v-for="(q, idx) in msg.suggestedQuestions" 
                   :key="idx" 
                   @click="handleSuggestedQuestion(q)">
                {{ q }}
              </div>
            </div>
            
            <!-- 消息操作按钮 -->
            <div class="message-actions" v-if="!msg.isStreaming">
              <button class="action-btn" @click="copyMessage(msg.content)" :title="'复制'">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
            
            <!-- 加载动画 -->
            <div v-if="msg.isStreaming" class="streaming-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, inject, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '../utils/api'
import { 
  getSessionMessages, 
  saveCurrentSessionId, 
  getCurrentSessionId,
  clearCurrentSessionId,
  type Message as SessionMessage 
} from '../services/session'

interface Message {
  content: string
  isUser: boolean
  isStreaming?: boolean
  suggestedQuestions?: string[]  // 推荐问题
}

const messages = ref<Message[]>([])
const messagesContainer = ref<HTMLElement | null>(null)
const sessionId = ref('')
const route = useRoute()
const router = useRouter()
const isStreaming = ref(false)  // 标记是否正在流式传输

// 获取全局的 sendMessage 方法
const chatSendMessage = inject<Ref<((message: string) => Promise<void>) | null>>('chatSendMessage')

// 推荐问题列表（从数据库获取）
const suggestedQuestions = ref<string[]>([])
const isLoadingQuestions = ref(false)

// 计算属性：是否是欢迎页面
const isWelcomePage = computed(() => {
  return !sessionId.value && messages.value.length === 0
})

console.log('✅ Chat组件已加载')

// 从API获取推荐问题
const loadSuggestedQuestions = async () => {
  try {
    isLoadingQuestions.value = true
    const response = await apiClient.get('/suggested-questions/list')
    // 响应拦截器已经返回了 res.data，所以 response 就是数组
    if (response && Array.isArray(response)) {
      suggestedQuestions.value = response.map((item: any) => item.question)
      console.log('✅ 加载推荐问题成功:', suggestedQuestions.value.length, '条')
    }
  } catch (error) {
    console.error('❌ 加载推荐问题失败:', error)
    // 如果API失败，使用默认问题
    suggestedQuestions.value = [
      "英语零基础先学单词还是语法？",
      "记单词总是忘，有没有高效方法？",
      "不敢开口说英语，怎么克服心理障碍？",
      "语法太杂看不懂，新手如何简易入门？",
      "听力完全听不懂，怎么一步步练？",
      "每天学多久英语？怎么合理安排时间？",
      "零基础要不要报网课？自学能学好吗？",
      "看美剧听英文歌能提升英语吗？",
      "学英语坚持不下来，怎么养成习惯？",
      "学会日常交流要多久？有进阶步骤吗？"
    ]
  } finally {
    isLoadingQuestions.value = false
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 处理推荐问题点击
const handleSuggestedQuestion = async (question: string) => {
  console.log('点击推荐问题:', question)
  if (chatSendMessage) {
    await chatSendMessage.value!(question)
  }
}

// 发送消息
const sendMessage = async (content: string) => {
  if (!content.trim()) return
  
  console.log(' 开始发送消息:', content)
  isStreaming.value = true  // 标记开始流式传输
  
  // 添加用户消息
  messages.value.push({
    content: content.trim(),
    isUser: true
  })
  
  // 添加AI消息占位
  messages.value.push({
    content: '',
    isUser: false,
    isStreaming: true
  })
  const aiMessageIndex = messages.value.length - 1
  
  await scrollToBottom()
  
  try {
    console.log('🌐 调用流式API...')
    
    // 检查token
    const token = localStorage.getItem('access_token')
    console.log('🔑 Token:', token ? '存在' : '不存在')
    
    if (!token) {
      throw new Error('未登录,请先登录')
    }
    
    // 调用流式API
    const response = await fetch(`${apiClient.defaults.baseURL}/chat_stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        question: content.trim(),
        session_id: sessionId.value || undefined  // 如果没有session_id，传undefined让后端创建
      })
    })
    
    console.log(' API响应状态:', response.status)
    
    // 如果是401，说明token无效
    if (response.status === 401) {
      console.error('❌ 认证失败，Token可能已过期')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      window.dispatchEvent(new CustomEvent('auth-expired'))
      throw new Error('登录已过期，请重新登录')
    }
    
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }
    
    // 从响应头获取session_id（如果是新创建的会话）
    const newSessionId = response.headers.get('X-Session-Id')
    const isNewSession = newSessionId && !sessionId.value
    if (isNewSession) {
      sessionId.value = newSessionId
      saveCurrentSessionId(sessionId.value)
      // 先不更新路由，等流式传输完成后再更新
      // 通知父组件刷新会话列表
      window.dispatchEvent(new CustomEvent('session-created', { detail: { sessionId: sessionId.value } }))
    }
    
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应')
    }
    
    const decoder = new TextDecoder()
    let accumulatedContent = ''
    let suggestedQuestions: string[] = []
    
    console.log('📡 开始接收流式数据...')
    console.log('🎯 AI消息索引:', aiMessageIndex)
    console.log(' 当前消息数组长度:', messages.value.length)
    
    while (true) {
      const { done, value } = await reader.read()
      
      if (done) {
        console.log('✅ 流式传输完成')
        break
      }
      
      const chunk = decoder.decode(value, { stream: true })
      
      // 解析SSE格式数据
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          
          // 检查是否是推荐问题
          if (data.startsWith('[SUGGESTED_QUESTIONS]')) {
            try {
              const questionsJson = data.replace('[SUGGESTED_QUESTIONS]', '')
              suggestedQuestions = JSON.parse(questionsJson)
              console.log('收到推荐问题:', suggestedQuestions)
            } catch (e) {
              console.error('解析推荐问题失败:', e)
            }
          } else if (data && data !== '[DONE]') {
            accumulatedContent += data
            console.log('📝 接收到数据片段:', data.substring(0, 50))
            console.log('📝 累积内容长度:', accumulatedContent.length)
            // 确保索引有效
            if (messages.value[aiMessageIndex]) {
              messages.value[aiMessageIndex].content = accumulatedContent
              console.log('✅ 已更新消息内容，当前长度:', messages.value[aiMessageIndex].content.length)
              await scrollToBottom()
            } else {
              console.error('❌ 消息索引无效！aiMessageIndex:', aiMessageIndex, '数组长度:', messages.value.length)
            }
          }
        }
      }
    }
    
    // 流式传输完成
    console.log('✅ 流式传输完成，最终内容长度:', accumulatedContent.length)
    if (messages.value[aiMessageIndex]) {
      messages.value[aiMessageIndex].isStreaming = false
      console.log('✅ 已设置 isStreaming = false')
      
      // 设置推荐问题
      if (suggestedQuestions.length > 0) {
        messages.value[aiMessageIndex].suggestedQuestions = suggestedQuestions
        console.log('✅ 已设置推荐问题:', suggestedQuestions)
      }
    } else {
      console.error('❌ 流式传输完成后，消息索引无效！')
    }
    
    console.log('✅ 消息处理完成')
    isStreaming.value = false  // 标记流式传输完成
    
    // 如果是新会话，在流式传输完成后更新路由并加载历史消息
    if (isNewSession && sessionId.value) {
      console.log('🔄 新会话创建完成，更新路由并加载历史消息')
      await router.push(`/chat/${sessionId.value}`)
      // 加载完整的历史消息（包括刚刚保存的AI回复）
      await loadHistoryMessages(sessionId.value)
    }
    
  } catch (error: any) {
    console.error('❌ 发送消息失败:', error)
    isStreaming.value = false  // 标记流式传输完成
    // 确保 aiMessageIndex 存在且有效
    if (aiMessageIndex !== undefined && messages.value[aiMessageIndex]) {
      messages.value[aiMessageIndex].content = '抱歉,发生了错误,请稍后重试。'
      messages.value[aiMessageIndex].isStreaming = false
    }
  }
}

// 加载历史消息
const loadHistoryMessages = async (sid: string) => {
  try {
    console.log('📚 加载历史消息, session_id:', sid)
    const historyMessages = await getSessionMessages(sid)
    
    // 转换消息格式
    messages.value = historyMessages.map((msg: SessionMessage) => ({
      content: msg.content,
      isUser: msg.role === 'user',
      isStreaming: false
    }))
    
    await scrollToBottom()
    console.log('✅ 历史消息加载完成, 共', messages.value.length, '条')
  } catch (error: any) {
    console.error('❌ 加载历史消息失败:', error)
    
    // 如果是401错误，说明token无效
    if (error.response?.status === 401) {
      console.error('❌ 认证失败，Token可能已过期')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      window.dispatchEvent(new CustomEvent('auth-expired'))
      messages.value = [{
        content: '登录已过期，请重新登录以查看历史消息',
        isUser: false,
        isStreaming: false
      }]
    } else {
      // 其他错误
      messages.value = [{
        content: '加载历史消息失败，请稍后重试',
        isUser: false,
        isStreaming: false
      }]
    }
  }
}

// 初始化会话
const initSession = async () => {
  // 从路由参数获取session_id
  const routeSessionId = route.params.id as string
  
  console.log('初始化会话, routeSessionId:', routeSessionId)
  
  if (routeSessionId) {
    // 如果路由中有session_id，使用它
    sessionId.value = routeSessionId
    saveCurrentSessionId(sessionId.value)
    await loadHistoryMessages(sessionId.value)
  } else {
    // 路由中没有session_id，这是新对话
    console.log(' 新对话，显示欢迎页面')
    sessionId.value = ''
    clearCurrentSessionId()
    messages.value = []  // 清空消息，显示欢迎页面
  }
  
  console.log('✅ 会话ID:', sessionId.value)
}

// 监听路由变化
watch(() => route.params.id, async (newId, oldId) => {
  console.log('路由变化: oldId=', oldId, 'newId=', newId)
  
  // 如果正在流式传输，不要加载历史消息（避免覆盖当前消息）
  if (isStreaming.value) {
    console.log('⚠️ 正在流式传输中，跳过历史消息加载')
    return
  }
  
  if (newId) {
    // 切换到有session_id的路由，加载历史消息
    sessionId.value = newId as string
    saveCurrentSessionId(sessionId.value)
    await loadHistoryMessages(sessionId.value)
  } else if (oldId && !newId) {
    // 从有session_id切换到无session_id（新对话）
    console.log('切换到新对话')
    sessionId.value = ''
    clearCurrentSessionId()
    messages.value = []  // 清空消息，显示欢迎页面
  }
})

// 组件挂载时注册sendMessage方法
onMounted(() => {
  initSession()
  loadSuggestedQuestions()  // 加载推荐问题
  
  // 将 sendMessage 方法注册到全局
  if (chatSendMessage) {
    chatSendMessage.value = sendMessage
    console.log('✅ sendMessage 方法已成功注册到全局')
  } else {
    console.error('❌ 无法获取 chatSendMessage inject')
  }
})

// 复制消息
const copyMessage = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    console.log('📋 已复制到剪贴板')
  } catch (error) {
    console.error('❌ 复制失败:', error)
  }
}

// 格式化消息(简单的换行处理)
const formatMessage = (content: string) => {
  return content.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--color-bg) 0%, var(--color-bg-secondary) 100%);
  overflow: hidden;
}

/* 欢迎页面样式 */
.welcome-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.welcome-content {
  max-width: 800px;
  width: 100%;
  text-align: center;
}

.welcome-title {
  font-size: 32px;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 40px;
  letter-spacing: 0.5px;
}

.suggested-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: center;
}

.question-chip {
  padding: 12px 20px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.question-chip:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 948px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.message-wrapper {
  width: 100%;
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease;
  width: 100%;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: center;
}

.message-content {
  max-width: 90%;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  font-size: 16px;
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
  transition: all 0.2s ease;
}

.user-message .message-content {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(45, 110, 255, 0.25);
}

.ai-message .message-content {
  background: var(--color-bg);
  color: var(--color-text-main);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}

.message-text {
  white-space: pre-wrap;
}

/* 推荐问题样式 */
.suggested-questions-inline {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}

.suggested-label {
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin-bottom: 8px;
  font-weight: 500;
}

.suggested-question-item {
  display: inline-block;
  padding: 8px 14px;
  margin: 4px 6px 4px 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--color-primary);
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1.4;
}

.suggested-question-item:hover {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 消息操作按钮 */
.message-actions {
  display: flex;
  gap: 6px;
  margin-top: 10px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.message-content:hover .message-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-btn svg {
  width: 14px;
  height: 14px;
}

/* 流式加载动画 */
.streaming-indicator {
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 8px 0;
}

.streaming-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  animation: bounce 1.4s infinite ease-in-out both;
}

.streaming-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.streaming-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .chat-messages {
    padding: 16px;
    gap: 16px;
  }
  
  .message-content {
    max-width: 90%;
    padding: 12px 14px;
    font-size: 13px;
  }
}
</style>
