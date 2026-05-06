<template>
  <div class="sidebar-overlay" v-if="isMobile && isOpen" @click="$emit('close')"></div>
  <div class="sidebar" :class="{ 'sidebar-open': isOpen, 'sidebar-mobile': isMobile }">
    <div class="sidebar-header">
      <div class="user-info">
        <div class="avatar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <span class="app-name">EnglishMate</span>
      </div>
    </div>

    <div class="sidebar-nav">
      <router-link 
        to="/chat" 
        class="nav-item" 
        active-class="active"
        :class="{ 'active': isActiveChatRoute }"
        @click="handleNavClick"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
        <span>新对话</span>
      </router-link>

      <router-link 
        to="/ai-create" 
        class="nav-item" 
        active-class="active"
        :class="{ 'active': isSpeakingPage }"
        @click="handleNavClick"
      >
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <span>口语训练</span>
      </router-link>

      <router-link to="/video-download" class="nav-item" active-class="active" @click="handleNavClick">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
        <span>视频下载</span>
      </router-link>
    </div>

    <div class="sidebar-section">
      <div class="section-title">{{ isSpeakingPage ? '口语训练历史' : isCloudPage ? '' : '历史对话' }}</div>
      <div class="history-list">
        <div v-if="isLoadingSessions" class="loading-sessions">
          <span>加载中...</span>
        </div>
        <div v-else-if="historyList.length === 0" class="empty-sessions">
          <span>{{ isSpeakingPage ? '暂无口语训练记录' : isCloudPage ? '' : '暂无历史对话' }}</span>
        </div>
        <div 
          v-else
          class="history-item" 
          :class="{ 'history-item-active': isActiveHistoryItem(item) }"
          v-for="item in historyList" 
          :key="item.id" 
          @click="handleHistoryItemClick(item)"
          @mouseenter="hoveredSessionId = item.session_id || String(item.id)"
          @mouseleave="hoveredSessionId = null"
        >
          <svg class="history-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          <a-tooltip :title="item.title" placement="top">
            <span class="history-text">{{ item.title }}</span>
          </a-tooltip>
          <div class="history-actions" :class="{ 'history-actions-visible': hoveredSessionId === (item.session_id || String(item.id)) }">
            <!-- 重命名按钮 -->
            <button 
              class="action-btn rename-btn"
              @click.stop="handleRename(item)"
              title="重命名"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
            </button>
            <!-- 删除按钮 -->
            <button 
              class="action-btn delete-btn"
              @click.stop="handleDeleteSession(item.session_id || String(item.id), item.title)"
              title="删除对话"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                <line x1="10" y1="11" x2="10" y2="17"/>
                <line x1="14" y1="11" x2="14" y2="17"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-footer">
      <div v-if="!isLoggedIn" class="login-prompt" @click="$emit('show-login')">
        <svg class="profile-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>点击登录</span>
      </div>
      <div v-else class="user-profile-wrapper">
        <div class="user-profile" @click="toggleMenu">
          <div class="avatar-small">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <span class="username-text">{{ username }}</span>
          <svg class="arrow-icon" :class="{ 'rotate': showMenu }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        
        <!-- 下拉菜单 -->
        <div v-if="showMenu" class="user-dropdown-menu" @click.stop>
          <div class="menu-item" @click="handleLogout">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
              <polyline points="16 17 21 12 16 7"/>
              <line x1="21" y1="12" x2="9" y2="12"/>
            </svg>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 确认退出对话框 -->
    <div v-if="showConfirmDialog" class="confirm-dialog-overlay" @click="closeConfirmDialog">
      <div class="confirm-dialog" @click.stop>
        <div class="dialog-header">
          <svg class="warning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <h3 class="dialog-title">确认退出登录？</h3>
          <button class="dialog-close" @click="closeConfirmDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog-content">
          <p>退出登录不会丢失任何数据，你仍可以登录此账号。</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeConfirmDialog">取消</button>
          <button class="btn-confirm" @click="confirmLogout">退出登录</button>
        </div>
      </div>
    </div>

    <!-- 确认删除会话对话框 -->
    <div v-if="showDeleteDialog" class="confirm-dialog-overlay" @click="closeDeleteDialog">
      <div class="confirm-dialog" @click.stop>
        <div class="dialog-header">
          <svg class="warning-icon delete-warning-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            <line x1="10" y1="11" x2="10" y2="17"/>
            <line x1="14" y1="11" x2="14" y2="17"/>
          </svg>
          <h3 class="dialog-title">确认删除对话？</h3>
          <button class="dialog-close" @click="closeDeleteDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog-content">
          <p>确定要删除「{{ sessionToDelete?.title }}」吗？此操作不可恢复。</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeDeleteDialog">取消</button>
          <button class="btn-confirm btn-delete" @click="confirmDelete">删除</button>
        </div>
      </div>
    </div>

    <!-- 重命名对话框 -->
    <div v-if="showRenameDialog" class="confirm-dialog-overlay" @click="closeRenameDialog">
      <div class="confirm-dialog rename-dialog" @click.stop>
        <div class="dialog-header">
          <svg class="warning-icon rename-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          <h3 class="dialog-title">编辑对话名称</h3>
          <button class="dialog-close" @click="closeRenameDialog">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog-content">
          <input 
            v-model="newTitle" 
            class="rename-input"
            placeholder="输入名称"
            @keyup.enter="confirmRename"
            autofocus
          />
        </div>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="closeRenameDialog">取消</button>
          <button class="btn-confirm" @click="confirmRename" :disabled="!newTitle.trim()">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getSessionList, deleteSession, renameSession, type Session, getSpeakingDialogueList, deleteSpeakingDialogue, renameSpeakingDialogue, type SpeakingDialogue } from '../services/session'
import { isAuthenticated } from '../services/auth'
import { message } from 'ant-design-vue'

const route = useRoute()

// 判断当前是否在口语训练页面（包括 /ai-create 和 /ai-create/:id）
const isSpeakingPage = computed(() => route.path === '/ai-create' || route.path.startsWith('/ai-create/'))

// 判断当前是否在视频下载页面
const isCloudPage = computed(() => route.path === '/video-download')

// 判断当前是否在chat页面（包括新对话和历史对话）
const isActiveChatRoute = computed(() => {
  return route.path === '/chat' || route.path.startsWith('/chat/')
})

// 获取当前激活的会话/对话ID
const activeSessionId = computed(() => {
  if (isSpeakingPage.value) {
    // 口语训练页面：从路由参数获取对话ID
    const id = route.params.id as string
    return id || null
  } else if (isActiveChatRoute.value) {
    // AI对话页面：从路由参数获取会话ID
    const id = route.params.id as string
    return id || null
  }
  return null
})

// 判断某个历史记录项是否为当前激活项
const isActiveHistoryItem = (item: HistoryItem): boolean => {
  if (!activeSessionId.value) return false
  
  const itemId = item.session_id || String(item.id)
  return itemId === activeSessionId.value
}

// 统一的历史列表类型
interface HistoryItem {
  id: number | string
  session_id?: string
  title: string
  created_at: string
}

interface Props {
  isOpen?: boolean
  isLoggedIn?: boolean
  username?: string
}

const props = withDefaults(defineProps<Props>(), {
  isOpen: true,
  isLoggedIn: false,
  username: '用户'
})

const emit = defineEmits<{
  close: []
  'show-login': []
  logout: []
  'load-session': [sessionId: string]
  'new-chat': []
  'load-speaking-history': [dialogueId: string]
}>()

const historyList = ref<HistoryItem[]>([])
const isLoadingSessions = ref(false)

const isMobile = ref(false)
const showMenu = ref(false)
const showConfirmDialog = ref(false)
const hoveredSessionId = ref<string | null>(null)
const showDeleteDialog = ref(false)
const sessionToDelete = ref<HistoryItem | null>(null)
const showRenameDialog = ref(false)
const sessionToRename = ref<HistoryItem | null>(null)
const newTitle = ref('')

// 加载历史列表（根据页面类型）
const loadSessions = async () => {
  console.log('🔍 Sidebar: loadSessions 被调用')
  console.log('🔍 isAuthenticated:', isAuthenticated())
  console.log('🔍 isSpeakingPage:', isSpeakingPage.value)
  
  if (!isAuthenticated()) {
    console.log('⚠️ 未登录，清空历史列表')
    historyList.value = []
    return
  }
  
  isLoadingSessions.value = true
  try {
    if (isSpeakingPage.value) {
      // 口语训练页面，加载对话历史
      console.log('📞 调用 getSpeakingDialogueList API...')
      const dialogues = await getSpeakingDialogueList()
      console.log('✅ 收到对话数据:', dialogues)
      historyList.value = dialogues.map(d => ({
        id: d.id,
        session_id: String(d.id),  // 使用id作为session_id
        title: d.title,
        created_at: d.created_at
      }))
      console.log('✅ 历史列表已更新，共', historyList.value.length, '条记录')
    } else if (isCloudPage.value) {
      // 视频下载页面，加载下载历史
      console.log('📥 视频下载页面，加载下载历史...')
      // TODO: 后续接入视频下载历史 API
      // 暂时显示空列表，由VideoDownload页面自己管理
      historyList.value = []
      console.log('✅ 下载历史列表已清空')
    } else {
      // AI英语助手页面，加载会话历史
      console.log('📞 调用 getSessionList API...')
      const sessions = await getSessionList()
      console.log('✅ 收到会话数据:', sessions)
      historyList.value = sessions
      console.log('✅ 历史列表已更新，共', historyList.value.length, '条记录')
    }
  } catch (error) {
    console.error('❌ 加载历史列表失败:', error)
  } finally {
    isLoadingSessions.value = false
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

const handleNavClick = () => {
  if (isMobile.value) {
    emit('close')
  }
}

// 点击新对话
const handleNewChat = () => {
  emit('new-chat')
  if (isMobile.value) {
    emit('close')
  }
}

// 点击历史会话
const handleSessionClick = (sessionId: string) => {
  emit('load-session', sessionId)
  if (isMobile.value) {
    emit('close')
  }
}

// 处理历史记录点击（根据页面类型）
const handleHistoryItemClick = (item: HistoryItem) => {
  if (isSpeakingPage.value) {
    // 口语训练页面，触发加载对话事件
    // 使用id作为dialogueId
    emit('load-speaking-history', String(item.id))
  } else if (isCloudPage.value) {
    // 视频下载页面， TODO: 后续接入下载历史点击逻辑
    console.log('📥 点击下载历史:', item.title)
    message.info('下载历史功能开发中')
  } else {
    // AI英语助手页面，加载会话
    if (item.session_id) {
      handleSessionClick(item.session_id)
    }
  }
}

const toggleMenu = () => {
  showMenu.value = !showMenu.value
}

const closeMenu = () => {
  showMenu.value = false
}

const handleLogout = () => {
  closeMenu()
  showConfirmDialog.value = true
}

const closeConfirmDialog = () => {
  showConfirmDialog.value = false
}

const confirmLogout = () => {
  closeConfirmDialog()
  emit('logout')
}

// 处理删除会话
const handleDeleteSession = (sessionId: string, title: string) => {
  sessionToDelete.value = { id: sessionId, session_id: sessionId, title, created_at: '' }
  showDeleteDialog.value = true
}

const closeDeleteDialog = () => {
  showDeleteDialog.value = false
  sessionToDelete.value = null
}

const confirmDelete = async () => {
  if (!sessionToDelete.value) return
  
  try {
    if (isSpeakingPage.value) {
      // 口语训练页面，删除对话
      await deleteSpeakingDialogue(Number(sessionToDelete.value.id))
    } else {
      // AI英语助手页面，删除会话
      if (sessionToDelete.value.session_id) {
        await deleteSession(sessionToDelete.value.session_id)
      }
    }
    // 删除成功后刷新列表
    await loadSessions()
    closeDeleteDialog()
    message.success('删除成功')
  } catch (error) {
    console.error('删除失败:', error)
    message.error('删除失败，请重试')
  }
}

// 重命名相关函数
const handleRename = (item: HistoryItem) => {
  sessionToRename.value = item
  newTitle.value = item.title
  showRenameDialog.value = true
}

const closeRenameDialog = () => {
  showRenameDialog.value = false
  sessionToRename.value = null
  newTitle.value = ''
}

const confirmRename = async () => {
  if (!sessionToRename.value || !newTitle.value.trim()) return
  
  try {
    if (isSpeakingPage.value) {
      // 口语训练页面，重命名对话
      await renameSpeakingDialogue(Number(sessionToRename.value.id), newTitle.value.trim())
    } else {
      // AI英语助手页面，重命名会话
      if (sessionToRename.value.session_id) {
        await renameSession(sessionToRename.value.session_id, newTitle.value.trim())
      }
    }
    // 重命名成功后刷新列表
    await loadSessions()
    closeRenameDialog()
    message.success('重命名成功')
  } catch (error) {
    console.error('重命名失败:', error)
    message.error('重命名失败，请重试')
  }
}

// 点击外部关闭菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-profile-wrapper')) {
    closeMenu()
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  document.addEventListener('click', handleClickOutside)
  
  // 加载会话列表
  loadSessions()
  
  // 监听刷新会话列表事件
  window.addEventListener('refresh-session-list', loadSessions)
})

// 监听登录状态变化
watch(() => props.isLoggedIn, (newValue) => {
  if (newValue) {
    loadSessions()
  } else {
    historyList.value = []
  }
})

// 监听路由变化，根据页面类型加载不同的历史
watch(() => route.path, () => {
  if (props.isLoggedIn) {
    loadSessions()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkMobile)
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('refresh-session-list', loadSessions)
})
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 99;
  backdrop-filter: blur(4px);
}

.sidebar {
  width: 260px;
  height: 100vh;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 100;
}

.sidebar-mobile {
  transform: translateX(-100%);
}

.sidebar-mobile.sidebar-open {
  transform: translateX(0);
}

/* Desktop sidebar toggle */
@media (min-width: 769px) {
  .sidebar:not(.sidebar-open) {
    transform: translateX(-100%);
  }
}

/* Desktop sidebar toggle */
@media (min-width: 769px) {
  .sidebar:not(.sidebar-open) {
    transform: translateX(-100%);
  }
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: transform 0.2s;
}

.avatar:hover {
  transform: scale(1.05);
}

.avatar svg {
  width: 20px;
  height: 20px;
}

.app-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
  letter-spacing: 0.5px;
}

.sidebar-nav {
  padding: 12px;
  flex-shrink: 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 4px;
  font-weight: 500;
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.nav-item.active {
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(45, 110, 255, 0.3);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.sidebar-section {
  padding: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.section-title {
  font-size: 12px;
  color: var(--color-text-placeholder);
  margin-bottom: 8px;
  padding: 0 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: calc(100vh - 280px);
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

/* Chrome, Safari and Opera */
.history-list::-webkit-scrollbar {
  display: none;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 13px;
  color: var(--color-text-secondary);
  position: relative;
}

.history-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
  transform: translateX(2px);
}

/* 当前激活的历史记录项 - 高亮背景 */
.history-item-active {
  background: rgba(45, 110, 255, 0.08);
  color: var(--color-primary);
  font-weight: 500;
}

.history-item-active:hover {
  background: rgba(45, 110, 255, 0.12);
  transform: none;
}

.history-item-active .history-icon {
  color: var(--color-primary);
}

.history-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  color: var(--color-text-placeholder);
}

.history-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.history-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transition: all 0.2s;
}

.history-actions-visible {
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.action-btn {
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  border: none;
  background: transparent;
  color: var(--color-text-placeholder);
  cursor: pointer;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
  padding: 0;
  margin: 0;
}

.action-btn:hover {
  background: rgba(45, 110, 255, 0.1);
  color: var(--color-primary);
}

.action-btn.delete-btn:hover {
  background: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.action-btn svg {
  width: 16px;
  height: 16px;
}

.loading-sessions,
.empty-sessions {
  padding: 20px 12px;
  text-align: center;
  color: var(--color-text-placeholder);
  font-size: 13px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--color-border);
  background: var(--color-bg);
  flex-shrink: 0;
}

.login-prompt {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--color-primary);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: all 0.2s;
  font-weight: 500;
}

.login-prompt:hover {
  background: var(--color-primary-light);
}

.user-profile-wrapper {
  position: relative;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 8px 12px;
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.user-profile:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.username-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.arrow-icon {
  width: 16px;
  height: 16px;
  transition: transform 0.2s;
}

.arrow-icon.rotate {
  transform: rotate(180deg);
}

/* 下拉菜单 */
.user-dropdown-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 8px;
  overflow: hidden;
  animation: slideUp 0.2s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.menu-item:hover {
  background: var(--color-bg-hover);
  color: #dc2626;
}

.menu-item svg {
  width: 16px;
  height: 16px;
}

/* 确认对话框 */
.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.confirm-dialog {
  background: var(--color-bg);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 420px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  position: relative;
}

.warning-icon {
  width: 24px;
  height: 24px;
  color: #f59e0b;
  flex-shrink: 0;
}

.dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  flex: 1;
}

.dialog-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.dialog-close:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.dialog-close svg {
  width: 18px;
  height: 18px;
}

.dialog-content {
  margin-bottom: 24px;
}

.dialog-content p {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.6;
}

.dialog-footer {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 重命名输入框 */
.rename-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-text-main);
  background: var(--color-bg);
  outline: none;
  transition: all 0.2s;
  box-sizing: border-box;
}

.rename-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(45, 110, 255, 0.1);
}

.rename-input::placeholder {
  color: var(--color-text-placeholder);
}

/* 重命名图标颜色 */
.rename-icon {
  color: var(--color-primary);
}

/* 确定按钮禁用状态 */
.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border: none;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
}

.btn-cancel:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.btn-confirm {
  background: #dc2626;
  color: white;
}

.btn-confirm:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-delete {
  background: #dc2626;
}

.btn-delete:hover {
  background: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.delete-warning-icon {
  color: #dc2626;
}

.profile-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.avatar-small {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.avatar-small svg {
  width: 16px;
  height: 16px;
}
</style>
