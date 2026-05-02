<template>
  <div class="auth-modal-overlay" v-if="visible" @click="handleOverlayClick">
    <div class="auth-modal" @click.stop>
      <button class="modal-close" @click="handleClose">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/>
          <line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>

      <div class="auth-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'login' }"
          @click="activeTab = 'login'"
        >
          登录
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'register' }"
          @click="activeTab = 'register'"
        >
          注册
        </button>
      </div>

      <div class="auth-content">
        <!-- Login Form -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="auth-form">
          <div class="form-group">
            <label class="form-label">用户名/邮箱</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              class="form-input"
              placeholder="请输入用户名或邮箱"
              required
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">密码</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              class="form-input"
              placeholder="请输入密码"
              required
            />
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="loginForm.remember" />
              <span>记住我</span>
            </label>
            <a href="#" class="forgot-password">忘记密码？</a>
          </div>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? '登录中...' : '登录' }}
          </button>
        </form>

        <!-- Register Form -->
        <form v-if="activeTab === 'register'" @submit.prevent="handleRegister" class="auth-form">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <input 
              v-model="registerForm.username" 
              type="text" 
              class="form-input"
              placeholder="请输入用户名"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label">邮箱</label>
            <input 
              v-model="registerForm.email" 
              type="email" 
              class="form-input"
              placeholder="请输入邮箱"
              required
            />
          </div>
          
          <div class="form-group">
            <label class="form-label">密码</label>
            <input 
              v-model="registerForm.password" 
              type="password" 
              class="form-input"
              placeholder="请输入密码（至少6位）"
              required
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label class="form-label">确认密码</label>
            <input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              class="form-input"
              placeholder="请再次输入密码"
              required
            />
          </div>

          <label class="agreement">
            <input type="checkbox" v-model="registerForm.agree" required />
            <span>我已阅读并同意 <a href="#">用户协议</a> 和 <a href="#">隐私政策</a></span>
          </label>

          <button type="submit" class="submit-btn" :disabled="isSubmitting">
            {{ isSubmitting ? '注册中...' : '注册' }}
          </button>
        </form>
      </div>

      <div class="auth-footer">
        <p v-if="activeTab === 'login'">
          还没有账号？
          <a href="#" @click.prevent="activeTab = 'register'" class="switch-link">立即注册</a>
        </p>
        <p v-else>
          已有账号？
          <a href="#" @click.prevent="activeTab = 'login'" class="switch-link">立即登录</a>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { register as registerAPI, login as loginAPI, saveAuth } from '../services/auth'
import { message } from 'ant-design-vue'

interface Props {
  visible: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  login: [data: any]
  register: [data: any]
}>()

const activeTab = ref('login')
const isSubmitting = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  remember: false
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false
})

const handleClose = () => {
  emit('update:visible', false)
  // 清空错误信息
  errorMessage.value = ''
}

const handleOverlayClick = () => {
  handleClose()
}

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    message.error('请输入用户名和密码')
    return
  }
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    const response = await loginAPI({
      username: loginForm.username,
      password: loginForm.password
    })
    
    // 保存认证信息
    saveAuth(response)
    
    // 如果选择记住我，可以设置更长的过期时间（这里简化处理）
    if (loginForm.remember) {
      // TODO: 可以实现remember me逻辑
    }
    
    console.log('Login success:', response)
    emit('login', response.user)
    handleClose()
    
    // 显示成功提示
    message.success('登录成功！')
  } catch (error: any) {
    console.error('Login failed:', error)
    errorMessage.value = error.message || '登录失败，请检查用户名和密码'
    message.error(errorMessage.value)
  } finally {
    isSubmitting.value = false
  }
}

const handleRegister = async () => {
  // 验证密码
  if (registerForm.password !== registerForm.confirmPassword) {
    message.error('两次密码输入不一致')
    return
  }
  
  // 验证密码长度
  if (registerForm.password.length < 6) {
    message.error('密码长度至少6位')
    return
  }
  
  // 验证是否同意协议
  if (!registerForm.agree) {
    message.error('请阅读并同意用户协议和隐私政策')
    return
  }
  
  isSubmitting.value = true
  errorMessage.value = ''
  
  try {
    const response = await registerAPI({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      full_name: registerForm.username // 使用用户名作为full_name
    })
    
    // 保存认证信息
    saveAuth(response)
    
    console.log('Register success:', response)
    emit('register', response.user)
    handleClose()
    
    // 显示成功提示
    message.success('注册成功！')
  } catch (error: any) {
    console.error('Register failed:', error)
    errorMessage.value = error.message || '注册失败，请稍后重试'
    message.error(errorMessage.value)
  } finally {
    isSubmitting.value = false
  }
}

// Reset form when tab changes
watch(activeTab, () => {
  isSubmitting.value = false
  errorMessage.value = ''
})
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
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

.auth-modal {
  background: var(--color-bg);
  border-radius: var(--radius-xl);
  width: 90%;
  max-width: 440px;
  padding: 42px;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-close {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  background: var(--color-bg-secondary);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}

.modal-close:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-main);
  transform: rotate(90deg);
}

.modal-close svg {
  width: 20px;
  height: 20px;
}

.auth-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--color-bg-secondary);
  padding: 4px;
  border-radius: var(--radius-lg);
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s;
}

.tab-btn.active {
  background: var(--color-bg);
  color: var(--color-text-main);
  box-shadow: var(--shadow-sm);
}

.tab-btn:hover:not(.active) {
  color: var(--color-text-main);
}

.auth-content {
  min-height: 280px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-main);
}

.form-input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--color-text-main);
  background: var(--color-bg-secondary);
  transition: all 0.2s;
  outline: none;
}

.form-input:focus {
  border-color: var(--color-primary);
  background: var(--color-bg);
  box-shadow: 0 0 0 3px rgba(45, 110, 255, 0.1);
}

.form-input::placeholder {
  color: var(--color-text-placeholder);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.remember-me input[type="checkbox"] {
  cursor: pointer;
}

.forgot-password {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.agreement {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-secondary);
  cursor: pointer;
}

.agreement input[type="checkbox"] {
  margin-top: 2px;
  cursor: pointer;
}

.agreement a {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 500;
}

.agreement a:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 12px 24px;
  border: none;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-hover) 100%);
  color: white;
  font-size: 15px;
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.25s;
  box-shadow: 0 4px 12px rgba(45, 110, 255, 0.3);
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(45, 110, 255, 0.4);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.switch-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
}

.switch-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .auth-modal {
    width: 95%;
    padding: 42px;
  }
  
  .auth-content {
    min-height: 240px;
  }
}
</style>
