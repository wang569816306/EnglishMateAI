<template>
  <div class="input-area">
    <div class="input-wrapper">
      <textarea
        v-model="message"
        class="message-input"
        placeholder="发消息..."
        @keydown.enter.prevent="handleSend"
        @input="autoResize"
        rows="1"
        ref="textareaRef"
        :disabled="isLoading"
      />
      
      <button 
        class="send-btn" 
        @click="handleSend"
        :disabled="!message.trim() || isLoading"
      >
        <svg v-if="!isLoading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
        <svg v-else class="loading-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10" stroke-dasharray="32" stroke-dashoffset="32">
            <animate attributeName="stroke-dashoffset" values="32;0" dur="1s" repeatCount="indefinite"/>
            <animate attributeName="stroke-dasharray" values="32;16" dur="1s" repeatCount="indefinite"/>
          </circle>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const message = ref('')
const isLoading = ref(false)
const textareaRef = ref<HTMLTextAreaElement | null>(null)

const props = defineProps<{
  loading?: boolean
}>()

watch(() => props.loading, (newVal) => {
  isLoading.value = newVal || false
})

const emit = defineEmits<{
  send: [message: string]
}>()

const handleSend = () => {
  console.log('InputArea handleSend 被调用')
  console.log('message.value:', message.value)
  console.log('isLoading.value:', isLoading.value)
  
  if (message.value.trim() && !isLoading.value) {
    console.log('发送消息:', message.value.trim())
    emit('send', message.value.trim())
    message.value = ''
    // 重置textarea高度
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  } else {
    console.log('消息为空或正在加载，不发送')
  }
}

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
  }
}
</script>

<style scoped>
.input-area {
  padding: 16px 24px 24px;
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
}

.input-wrapper {
  max-width: 900px;
  margin: 0 auto;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: 12px 18px;
  box-shadow: var(--shadow-md);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 52px;
}

.input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-md), 0 0 0 3px rgba(45, 110, 255, 0.1);
}

.message-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-size: 15px;
  line-height: 1.6;
  color: var(--color-text-main);
  font-family: inherit;
  min-height: 24px;
  max-height: 200px;
  background: transparent;
  padding: 0;
}

.message-input::placeholder {
  color: var(--color-text-placeholder);
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 6px rgba(45, 110, 255, 0.3);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 4px 10px rgba(45, 110, 255, 0.4);
}

.send-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

.send-btn svg {
  width: 18px;
  height: 18px;
}

.loading-icon {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 768px) {
  .input-area {
    padding: 12px 16px 16px;
  }
  
  .input-wrapper {
    padding: 12px 14px;
  }
  
  .message-input {
    font-size: 14px;
  }
  
  .send-btn {
    width: 32px;
    height: 32px;
  }
  
  .send-btn svg {
    width: 16px;
    height: 16px;
  }
}
</style>
