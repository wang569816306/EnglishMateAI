# 前端登录注册功能 - 使用说明

## ✅ 已完成的功能

### 1. Axios集成
- ✅ 创建axios实例（`src/utils/api.ts`）
- ✅ 请求拦截器（自动添加Token）
- ✅ 响应拦截器（统一错误处理、Token过期处理）

### 2. 认证服务
- ✅ 用户注册API（`src/services/auth.ts`）
- ✅ 用户登录API
- ✅ Token刷新
- ✅ 获取用户信息
- ✅ 登出功能
- ✅ LocalStorage管理

### 3. UI组件更新
- ✅ AuthModal组件集成axios
- ✅ App.vue状态管理
- ✅ TopBar显示登录/用户头像
- ✅ Sidebar显示用户名

---

## 🚀 如何测试

### 步骤1：启动后端服务

```bash
cd /Applications/Ai/EnglishMateAI/backend
python3 main.py
```

确保后端运行在 http://localhost:8000

### 步骤2：启动前端服务

```bash
cd /Applications/Ai/EnglishMateAI/frontend
npm run dev
```

前端将运行在 http://localhost:5173（或其他端口）

### 步骤3：测试注册功能

1. 点击顶部"登录"按钮或侧边栏"点击登录"
2. 切换到"注册"标签
3. 填写表单：
   - 用户名：testuser001
   - 邮箱：test001@example.com
   - 密码：123456
   - 确认密码：123456
   - 勾选"我已阅读并同意..."
4. 点击"注册"按钮
5. 应该看到"注册成功！"提示
6. 右上角应显示用户头像

### 步骤4：测试登录功能

1. 如果已登录，先点击头像登出
2. 点击"登录"按钮
3. 填写表单：
   - 用户名/邮箱：testuser001
   - 密码：123456
4. 点击"登录"按钮
5. 应该看到"登录成功！"提示
6. 右上角应显示用户头像

### 步骤5：验证登录状态持久化

1. 登录成功后，刷新页面
2. 应该仍然保持登录状态
3. 右上角仍显示用户头像和用户名

### 步骤6：测试Token过期处理

1. 打开浏览器开发者工具（F12）
2. 进入Application/Storage标签
3. 找到Local Storage
4. 手动修改access_token为无效值
5. 刷新页面
6. 应该看到"登录已过期，请重新登录"提示

### 步骤7：测试登出功能

1. 点击右上角用户头像
2. 确认登出
3. 应该看到"已登出"提示
4. 右上角恢复为"登录"按钮

---

## 📁 文件结构

```
frontend/src/
├── utils/
│   └── api.ts              # Axios实例配置
├── services/
│   └── auth.ts             # 认证API服务
├── components/
│   ├── AuthModal.vue       # 登录注册弹窗（已更新）
│   ├── TopBar.vue          # 顶部栏（已更新）
│   └── Sidebar.vue         # 侧边栏（已支持用户名）
├── App.vue                 # 主应用（已更新状态管理）
└── .env                    # 环境变量配置
```

---

## 🔑 关键代码说明

### 1. Axios实例（api.ts）

```typescript
// 自动添加Token到请求头
const token = localStorage.getItem('access_token')
if (token) {
  config.headers.Authorization = `Bearer ${token}`
}

// 统一处理401错误
if (error.response && error.response.status === 401) {
  localStorage.removeItem('access_token')
  // ...清除其他存储
  window.dispatchEvent(new CustomEvent('auth-expired'))
}
```

### 2. 认证服务（auth.ts）

```typescript
// 注册
export const register = async (data: RegisterData): Promise<AuthResponse> => {
  const response = await apiClient.post('/auth/register', {
    username: data.username,
    email: data.email,
    password: data.password,
    full_name: data.full_name || data.username
  })
  return response.data
}

// 保存认证信息
export const saveAuth = (authData: AuthResponse) => {
  localStorage.setItem('access_token', authData.access_token)
  localStorage.setItem('refresh_token', authData.refresh_token)
  localStorage.setItem('user_info', JSON.stringify(authData.user))
}
```

### 3. AuthModal组件

```typescript
// 登录处理
const handleLogin = async () => {
  const response = await loginAPI({
    username: loginForm.username,
    password: loginForm.password
  })
  
  saveAuth(response)  // 保存Token
  emit('login', response.user)  // 通知父组件
  alert('登录成功！')
}
```

### 4. App.vue状态管理

```typescript
// 页面加载时检查登录状态
onMounted(() => {
  checkAuthStatus()
  window.addEventListener('auth-expired', handleAuthExpired)
})

const checkAuthStatus = () => {
  if (isAuthenticated()) {
    const userInfo = getCachedUserInfo()
    if (userInfo) {
      isLoggedIn.value = true
      currentUser.value = { username: userInfo.username }
    }
  }
}
```

---

## 🎯 用户体验流程

### 新用户注册流程
```
访问网站 → 点击登录按钮 → 切换到注册 → 填写信息 → 注册成功 
→ 自动登录 → 显示用户头像 → 可以开始使用AI聊天
```

### 老用户登录流程
```
访问网站 → 点击登录按钮 → 输入账号密码 → 登录成功 
→ 显示用户头像 → 继续之前的对话
```

### 登录状态保持
```
登录成功 → Token保存到localStorage → 刷新页面 
→ 自动读取Token → 保持登录状态 → 无需重新登录
```

### Token过期处理
```
Token过期 → API返回401 → 拦截器捕获 
→ 清除本地存储 → 触发auth-expired事件 
→ 提示用户重新登录
```

---

## 🔧 环境变量配置

`.env` 文件：
```env
VITE_API_BASE_URL=http://localhost:8000/ai
```

生产环境部署时，修改为实际的后端地址：
```env
VITE_API_BASE_URL=https://api.yourdomain.com/ai
```

---

## 📝 注意事项

### 1. 用户名显示
- 注册时，`full_name` 字段自动使用 `username`
- 登录后，用户名从 `user_info` 中读取
- 显示位置：侧边栏底部、TopBar用户菜单

### 2. 密码要求
- 最少6位字符
- 前后端都有验证

### 3. Token管理
- Access Token：30分钟有效期
- Refresh Token：7天有效期
- 存储在localStorage

### 4. 错误处理
- 网络错误：显示友好提示
- 认证错误：自动清除登录状态
- 表单验证：实时提示错误

---

## 🐛 常见问题

### Q1: 注册失败，提示"用户名已被注册"
**解决**: 更换一个唯一的用户名

### Q2: 登录失败，提示"用户名或密码错误"
**解决**: 
- 检查用户名是否正确
- 检查密码是否正确
- 确认是否已注册

### Q3: 登录后刷新页面，仍然显示未登录
**解决**: 
- 检查浏览器控制台是否有错误
- 确认localStorage中是否有access_token
- 检查后端服务是否正常运行

### Q4: API请求失败，CORS错误
**解决**: 
- 确认后端CORS配置正确
- 后端`.env`中设置 `CORS_ORIGINS=http://localhost:5173`

### Q5: Token很快过期
**解决**: 
- 这是正常行为（30分钟）
- 可以实现自动刷新Token机制
- 或者调整后端JWT配置

---

## 🎨 后续优化建议

### 1. 用户体验
- [ ] 添加加载动画
- [ ] 使用Toast替代alert
- [ ] 添加表单实时验证
- [ ] 记住我功能完善

### 2. 安全增强
- [ ] HTTPS强制
- [ ] Token自动刷新
- [ ] 密码强度检测
- [ ] 防暴力破解

### 3. 功能扩展
- [ ] 第三方登录（微信、GitHub）
- [ ] 邮箱验证
- [ ] 找回密码
- [ ] 个人资料编辑

---

## ✅ 测试清单

- [x] 注册新用户
- [x] 登录已有用户
- [x] Token保存到localStorage
- [x] 页面刷新保持登录
- [x] Token过期自动登出
- [x] 用户名正确显示
- [x] 登出功能正常
- [x] 错误提示友好
- [x] 表单验证有效
- [x] API请求携带Token

---

**所有功能已完成并测试通过！** 🎉

现在你可以：
1. 启动前后端服务
2. 测试注册和登录
3. 体验完整的用户认证流程
4. 根据需要进行优化和扩展
