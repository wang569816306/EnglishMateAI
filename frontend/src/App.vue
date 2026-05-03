<script setup lang="ts">
import Sidebar from './components/Sidebar.vue'
import InputArea from './components/InputArea.vue'
import TopBar from './components/TopBar.vue'
import AuthModal from './components/AuthModal.vue'
import { ref, computed, onMounted, watch, provide } from 'vue'
import { useRouter } from 'vue-router'
import { getCachedUserInfo, clearAuth, isAuthenticated, logout as logoutAPI } from './services/auth'
import { message } from 'ant-design-vue'

const router = useRouter()
const currentRoute = router.currentRoute

// 根据屏幕宽度初始化侧边栏状态
const isMobile = window.innerWidth <= 768
const isSidebarOpen = ref(!isMobile)
const showAuthModal = ref(false)
const isLoggedIn = ref(false)
const currentUser = ref<{ username: string } | null>(null)
const isLoading = ref(false)

// 使用 provide/inject 模式来传递 sendMessage 方法
const chatSendMessage = ref<((message: string) => Promise<void>) | null>(null)
provide('chatSendMessage', chatSendMessage as any)

// 页面加载时检查登录状态
onMounted(() => {
  checkAuthStatus()
  
  // 监听Token过期事件
  window.addEventListener('auth-expired', handleAuthExpired)
  
  // 监听新会话创建事件
  window.addEventListener('session-created', handleSessionCreated)
})

const checkAuthStatus = () => {
  if (isAuthenticated()) {
    const userInfo = getCachedUserInfo()
    if (userInfo && userInfo.username) {
      isLoggedIn.value = true
      currentUser.value = { username: userInfo.username }
      console.log('User logged in:', userInfo.username)
    } else {
      console.warn('用户信息不完整，清除认证状态')
      clearAuth()
    }
  }
}

const handleAuthExpired = () => {
  console.log('Auth token expired')
  isLoggedIn.value = false
  currentUser.value = null
  // 弹出登录框
  showAuthModal.value = true
}

// 处理新会话创建
const handleSessionCreated = (event: any) => {
  console.log('新会话创建:', event.detail?.sessionId)
  // 刷新侧边栏的会话列表
  // 通过重新加载当前路由来触发Sidebar组件的watch
  const sidebarElement = document.querySelector('.sidebar')
  if (sidebarElement) {
    // 触发一个自定义事件让Sidebar重新加载会话列表
    window.dispatchEvent(new CustomEvent('refresh-session-list'))
  }
}

const pageTitle = computed(() => {
  const path = currentRoute.value.path
  if (path === '/' || path.startsWith('/chat')) {
    // 如果有session_id参数，显示"历史对话",否则显示"新对话"
    const hasSessionId = path.startsWith('/chat/') && path.length > 6
    return hasSessionId ? '历史对话' : '新对话'
  }
  if (path === '/ai-create' || path.startsWith('/ai-create/')) return '口语训练'
  if (path === '/cloud') return '视频下载'
  return '新对话'
})

// 监听路由变化,只在聊天页面显示输入框
const showInputArea = computed(() => {
  const path = currentRoute.value.path
  return path === '/' || path.startsWith('/chat')
})

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const closeSidebar = () => {
  isSidebarOpen.value = false
}

const showLogin = () => {
  showAuthModal.value = true
}

const showUserMenu = () => {
  // TODO: 实现用户菜单（包含登出功能）
  const confirmLogout = confirm('确定要登出吗？')
  if (confirmLogout) {
    handleLogout()
  }
}

const handleLogout = async () => {
  try {
    // 调用后端登出接口
    await logoutAPI()
    
    // 清除本地状态
    isLoggedIn.value = false
    currentUser.value = null
    
    // 显示成功提示
    message.success('已成功退出登录')
    
    console.log('User logged out')
  } catch (error) {
    console.error('Logout failed:', error)
    message.error('退出登录失败，请重试')
  }
}

const handleLogin = (user: any) => {
  console.log('Login success:', user)
  if (user && user.username) {
    isLoggedIn.value = true
    currentUser.value = { username: user.username }
  } else {
    console.error('登录响应中缺少用户信息', user)
    message.error('登录失败：用户信息不完整')
  }
}

const handleRegister = (user: any) => {
  console.log('Register success:', user)
  if (user && user.username) {
    // 注册成功后自动登录
    isLoggedIn.value = true
    currentUser.value = { username: user.username }
  } else {
    console.error('注册响应中缺少用户信息', user)
    message.error('注册失败：用户信息不完整')
  }
}

const handleSend = async (message: string) => {
  console.log('App.vue handleSend 被调用:', message)
  console.log('chatSendMessage.value:', chatSendMessage.value)
  
  if (!isAuthenticated()) {
    console.log('未登录，弹出登录框')
    showAuthModal.value = true
    return
  }
  
  if (!chatSendMessage.value) {
    console.error('chatSendMessage 未设置')
    return
  }
  
  isLoading.value = true
  console.log('isLoading 设置为 true')
  
  try {
    console.log('开始调用 chatSendMessage')
    await chatSendMessage.value(message)
    console.log('chatSendMessage 调用完成')
  } catch (error) {
    console.error('发送消息失败:', error)
  } finally {
    isLoading.value = false
    console.log('isLoading 设置为 false')
  }
}

// 加载历史会话
const handleLoadSession = (sessionId: string) => {
  console.log('加载会话:', sessionId)
  // 导航到该会话
  router.push(`/chat/${sessionId}`)
}

// 创建新对话
const handleNewChat = () => {
  console.log('创建新对话')
  // 导航到新对话页面
  router.push('/chat')
}

// 加载口语训练历史
const handleLoadSpeakingHistory = (dialogueId: string) => {
  console.log('加载口语训练对话:', dialogueId)
  // 触发事件，让AICreate页面加载对话
  window.dispatchEvent(new CustomEvent('load-speaking-dialogue', { 
    detail: { dialogueId } 
  }))
}
</script>

<template>
  <div class="app-container">
    <Sidebar 
      :is-open="isSidebarOpen" 
      :is-logged-in="isLoggedIn"
      :username="currentUser?.username || '用户'"
      @close="closeSidebar"
      @show-login="showLogin"
      @logout="handleLogout"
      @load-session="handleLoadSession"
      @new-chat="handleNewChat"
      @load-speaking-history="handleLoadSpeakingHistory"
    />
    <div class="main-content" :class="{ 'main-with-sidebar': isSidebarOpen }">
      <TopBar 
        :title="pageTitle" 
        :is-logged-in="isLoggedIn"
        @toggle-sidebar="toggleSidebar" 
        @show-login="showLogin"
        @show-user-menu="showUserMenu"
        @new-chat="handleNewChat"
      />
      <div class="content-wrapper">
        <!-- 使用 v-slot 获取 router-view 的子组件 -->
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </div>
      <InputArea 
        v-if="showInputArea" 
        @send="handleSend" 
        :loading="isLoading"
      />
    </div>
    
    <!-- Auth Modal -->
    <AuthModal 
      v-model:visible="showAuthModal"
      @login="handleLogin"
      @register="handleRegister"
    />
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: white;
  margin-left: 0;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.main-content.main-with-sidebar {
  margin-left: 260px;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
  }
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
</style>
