<template>
  <div class="top-bar">
    <div class="top-bar-left">
      <button class="menu-toggle-btn" @click="$emit('toggle-sidebar')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <line x1="9" y1="3" x2="9" y2="21"/>
        </svg>
      </button>
      <button class="new-chat-btn" @click="$emit('new-chat')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 20h9"/>
          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
        </svg>
      </button>
    </div>
    
    <div class="top-bar-center">
      <h1 class="top-bar-title">{{ title }}</h1>
      <p class="top-bar-subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="top-bar-right">
      <button v-if="!isLoggedIn" class="login-btn" @click="$emit('show-login')">
        登录
      </button>
      <slot name="right"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  subtitle?: string
  isLoggedIn?: boolean
}

withDefaults(defineProps<Props>(), {
  subtitle: '内容由豆包 AI 生成，请仔细甄别',
  isLoggedIn: false
})

defineEmits<{
  'toggle-sidebar': []
  'show-login': []
  'show-user-menu': []
  'new-chat': []
}>()
</script>

<style scoped>
.top-bar {
  height: 56px;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.top-bar-left,
.top-bar-right {
  min-width: 40px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.top-bar-center {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.top-bar-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-main);
  margin: 0;
  line-height: 1.2;
}

.top-bar-subtitle {
  font-size: 11px;
  color: var(--color-text-placeholder);
  margin: 2px 0 0 0;
}

.menu-toggle-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.menu-toggle-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
}

.menu-toggle-btn svg {
  width: 18px;
  height: 18px;
}

.new-chat-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-primary);
}

.new-chat-btn svg {
  width: 18px;
  height: 18px;
}

.login-btn {
  padding: 8px 20px;
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: white;
  font-size: 14px;
  font-weight: 600;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 2px 8px rgba(45, 110, 255, 0.3);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45, 110, 255, 0.4);
}

.login-btn:active {
  transform: translateY(0);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.user-avatar:hover {
  transform: scale(1.05);
}

.user-avatar svg {
  width: 20px;
  height: 20px;
}

@media (min-width: 769px) {
  .top-bar-left {
    width: auto;
  }
}

@media (max-width: 768px) {
  .top-bar {
    height: 48px;
  }
  
  .top-bar-title {
    font-size: 14px;
  }
  
  .top-bar-subtitle {
    font-size: 10px;
  }
}
</style>
