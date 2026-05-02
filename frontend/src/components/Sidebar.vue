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
      <div class="nav-item" @click="handleNewChat">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
        <span>新对话</span>
      </div>

      <router-link to="/ai-create" class="nav-item" active-class="active" @click="handleNavClick">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2L2 7l10 5 10-5-10-5z"/>
          <path d="M2 17l10 5 10-5"/>
          <path d="M2 12l10 5 10-5"/>
        </svg>
        <span>AI 创作</span>
      </router-link>

      <router-link to="/cloud" class="nav-item" active-class="active" @click="handleNavClick">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span>云盘</span>
      </router-link>
    </div>

    <div class="sidebar-section">
      <div class="section-title">历史对话</div>
      <div class="history-list">
        <div v-if="isLoadingSessions" class="loading-sessions">
          <span>加载中...</span>
        </div>
        <div v-else-if="historyList.length === 0" class="empty-sessions">
          <span>暂无历史对话</span>
        </div>
        <div 
          v-else
          class="history-item" 
          v-for="item in historyList" 
          :key="item.id" 
          @click="handleSessionClick(item.session_id)"
        >
          <svg class="history-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          <span class="history-text">{{ item.title }}</span>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, onBeforeUnmount, watch } from 'vue'
import { getSessionList, type Session } from '../services/session'
import { isAuthenticated } from '../services/auth'

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
}>()

const historyList = ref<Session[]>([])
const isLoadingSessions = ref(false)

const isMobile = ref(false)
const showMenu = ref(false)
const showConfirmDialog = ref(false)

// 加载会话列表
const loadSessions = async () => {
  if (!isAuthenticated()) {
    historyList.value = []
    return
  }
  
  isLoadingSessions.value = true
  try {
    const sessions = await getSessionList()
    historyList.value = sessions
  } catch (error) {
    console.error('加载会话列表失败:', error)
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
  overflow-y: auto;
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
}

.history-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
  transform: translateX(2px);
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

.profile-icon {
  width: 16px;
  height: 16px;
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
