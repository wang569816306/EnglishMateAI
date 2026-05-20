<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <div class="message-wrapper" v-for="(msg, index) in messages" :key="index">
        <!-- 用户消息 -->
        <div v-if="msg.isUser" class="message-item user-message">
          <div class="message-content">{{ msg.content }}</div>
        </div>
        
        <!-- AI消息 -->
        <div v-else class="message-item ai-message">
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            
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
import { ref, nextTick, onMounted, inject, watch } from 'vue'
import { useRoute } from 'vue-router'
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
}

const messages = ref<Message[]>([])
const messagesContainer = ref<HTMLElement | null>(null)
const sessionId = ref('')
const route = useRoute()

console.log('✅ Chat组件已加载')

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 发送消息
const sendMessage = async (content: string) => {
  if (!content.trim()) return
  
  console.log('📤 开始发送消息:', content)
  
  // 添加用户消息
  messages.value.push({
    content: content.trim(),
    isUser: true
  })
  
  // 添加AI消息占位
  const aiMessageIndex = messages.value.length
  messages.value.push({
    content: '',
    isUser: false,
    isStreaming: true
  })
  
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
        session_id: sessionId.value
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
    
    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法读取响应')
    }
    
    const decoder = new TextDecoder()
    let accumulatedContent = ''
    
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
          if (data && data !== '[DONE]') {
            accumulatedContent += data
            messages.value[aiMessageIndex].content = accumulatedContent
            await scrollToBottom()
          }
        }
      }
    }
    
    // 流式传输完成
    messages.value[aiMessageIndex].isStreaming = false
    console.log('✅ 消息处理完成')
    
  } catch (error: any) {
    console.error('❌ 发送消息失败:', error)
    messages.value[aiMessageIndex].content = '抱歉,发生了错误,请稍后重试。'
    messages.value[aiMessageIndex].isStreaming = false
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
  } catch (error) {
    console.error('❌ 加载历史消息失败:', error)
  }
}

// 初始化会话
const initSession = () => {
  // 从路由参数获取session_id
  const routeSessionId = route.params.id as string
  
  if (routeSessionId) {
    // 如果路由中有session_id，使用它
    sessionId.value = routeSessionId
    saveCurrentSessionId(sessionId.value)
    loadHistoryMessages(sessionId.value)
  } else {
    // 否则尝试从localStorage恢复
    const savedSessionId = getCurrentSessionId()
    if (savedSessionId) {
      sessionId.value = savedSessionId
      loadHistoryMessages(sessionId.value)
    } else {
      // 如果没有保存的会话，创建一个新的（在第一次发送消息时）
      sessionId.value = ''
      console.log('🆕 新会话，将在首次发送消息时创建')
    }
  }
  
  console.log(' 会话ID:', sessionId.value)
}

// 监听路由变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    sessionId.value = newId as string
    saveCurrentSessionId(sessionId.value)
    loadHistoryMessages(sessionId.value)
  }
})

// 组件挂载时注册sendMessage方法
onMounted(() => {
  initSession()
  
  // 将 sendMessage 方法注册到全局
  const chatSendMessage = inject<Ref<((message: string) => Promise<void>) | null>>('chatSendMessage')
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

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
}

.message-wrapper {
  width: 100%;
}

.message-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  animation: fadeIn 0.3s ease;
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
  justify-content: flex-start;
}

.message-content {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: var(--radius-lg);
  font-size: 14px;
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
    max-width: 85%;
    padding: 12px 14px;
    font-size: 13px;
  }
}
</style>
