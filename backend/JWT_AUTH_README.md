# JWT认证系统 - 功能说明

## 📋 概述

本次更新为EnglishMateAI后端添加了完整的JWT用户认证系统，包括注册、登录、Token刷新等功能。

---

## ✨ 新增功能

### 1. 用户认证系统
- ✅ 用户注册（邮箱验证）
- ✅ 用户登录（支持用户名/邮箱）
- ✅ JWT Token生成和验证
- ✅ Access Token刷新机制
- ✅ 密码加密存储（bcrypt）
- ✅ 获取当前用户信息
- ✅ 修改密码
- ✅ 用户登出

### 2. 数据库支持
- ✅ SQLite（开发环境）
- ✅ PostgreSQL（生产环境推荐）
- ✅ SQLAlchemy ORM
- ✅ 自动表结构创建

### 3. 安全特性
- ✅ 密码bcrypt加密
- ✅ JWT双Token机制（Access + Refresh）
- ✅ Token过期控制
- ✅ API端点保护
- ✅ CORS跨域配置

---

## 🗄️ 数据库设计

### 用户表 (users)
```sql
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- hashed_password: 加密密码
- full_name: 真实姓名
- avatar_url: 头像URL
- is_active: 账户状态
- is_verified: 邮箱验证状态
- created_at: 创建时间
- updated_at: 更新时间
```

### 会话表 (sessions)
```sql
- id: 主键
- user_id: 用户ID
- session_id: 会话标识
- title: 会话标题
- created_at: 创建时间
- updated_at: 更新时间
```

### 消息表 (messages)
```sql
- id: 主键
- session_id: 会话ID
- role: 角色（user/assistant）
- content: 消息内容
- created_at: 创建时间
```

---

## 🔐 认证流程

### 注册流程
```
1. 用户提交注册信息（用户名、邮箱、密码）
2. 后端验证数据合法性
3. 检查用户名/邮箱是否已存在
4. 使用bcrypt加密密码
5. 保存用户到数据库
6. 生成JWT Token
7. 返回用户信息和Token
```

### 登录流程
```
1. 用户提交登录凭证（用户名/邮箱 + 密码）
2. 查询用户记录
3. 验证密码（bcrypt.compare）
4. 检查账户状态
5. 生成Access Token（30分钟有效）
6. 生成Refresh Token（7天有效）
7. 返回Token
```

### Token刷新流程
```
1. 客户端发送Refresh Token
2. 后端验证Token有效性
3. 检查用户状态
4. 生成新的Access Token
5. 返回新Token
```

### API调用流程
```
1. 客户端在请求头携带Token
   Authorization: Bearer <access_token>
2. 后端验证Token签名和有效期
3. 从数据库获取用户信息
4. 执行业务逻辑
5. 返回结果
```

---

## 📡 API接口

### 基础URL
```
http://localhost:8000/ai
```

### 1. 用户注册
**POST** `/auth/register`

**请求体:**
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "123456",
  "full_name": "测试用户"
}
```

**响应:**
```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "full_name": "测试用户"
    },
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 2. 用户登录
**POST** `/auth/login`

**请求体:**
```json
{
  "username": "testuser",  // 可以是用户名或邮箱
  "password": "123456"
}
```

**响应:** 同注册响应

### 3. 刷新Token
**POST** `/auth/refresh`

**请求体:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**响应:**
```json
{
  "code": 200,
  "msg": "刷新成功",
  "data": {
    "access_token": "new_eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 4. 获取当前用户
**GET** `/auth/me`

**请求头:**
```
Authorization: Bearer <access_token>
```

**响应:**
```json
{
  "code": 200,
  "msg": "获取成功",
  "data": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "测试用户",
    "avatar_url": null
  }
}
```

### 5. 修改密码
**POST** `/auth/change-password`

**请求头:**
```
Authorization: Bearer <access_token>
```

**请求体:**
```json
{
  "old_password": "123456",
  "new_password": "newpassword"
}
```

### 6. AI聊天（需要认证）
**POST** `/chat`

**请求头:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体:**
```json
{
  "question": "How to use present perfect tense?",
  "session_id": "my_session"
}
```

---

## 🔧 配置说明

### 环境变量 (.env)

```env
# JWT配置
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 数据库配置
# SQLite（开发）
DATABASE_URL=sqlite:///./english_mate.db

# PostgreSQL（生产）
# DATABASE_URL=postgresql://user:password@localhost:5432/english_mate
```

### 生成安全的JWT密钥

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境

```bash
cp .env.example .env
# 编辑 .env 文件，配置必要参数
```

### 3. 初始化数据库

```bash
python init_db.py
```

### 4. 启动服务

```bash
python main.py
```

### 5. 测试功能

```bash
python test_auth.py
```

---

## 📊 架构变化

### 之前
```
用户 → API Key认证 → Chat Agent → Redis记忆 → RAG检索
```

### 现在
```
用户 → JWT认证 → Chat Agent → Redis记忆 + 数据库持久化 → RAG检索
```

### 关键改进
1. **认证方式**: API Key → JWT（更安全、更灵活）
2. **数据存储**: 纯Redis → Redis + 关系型数据库
3. **会话管理**: 临时存储 → 持久化存储
4. **用户管理**: 无 → 完整的用户系统

---

## 🔄 向后兼容

### API Key认证仍然可用
原有的API Key认证模块保留在 `app/auth/api_key_auth.py`，如果需要可以切换回去。

### 迁移建议
1. 前端改用JWT Token认证
2. 在请求头中使用 `Authorization: Bearer <token>`
3. 实现Token自动刷新机制
4. 处理Token过期情况

---

## 🛡️ 安全最佳实践

### 1. 生产环境必须做的
- [ ] 修改 `JWT_SECRET_KEY` 为强随机字符串
- [ ] 使用PostgreSQL替代SQLite
- [ ] 启用HTTPS
- [ ] 配置CORS白名单
- [ ] 设置合理的Token过期时间
- [ ] 定期备份数据库

### 2. 密码策略建议
- 最小长度：6字符（可调整为8-12）
- 包含大小写字母、数字、特殊字符
- 禁止常见弱密码
- 实施密码历史检查

### 3. Token管理
- Access Token：短期（15-30分钟）
- Refresh Token：长期（7-30天）
- 实现Token黑名单机制（可选）
- 登出时清除客户端Token

---

## 🐛 常见问题

### Q1: 如何重置数据库？
```bash
# SQLite
rm english_mate.db
python init_db.py

# PostgreSQL
DROP DATABASE english_mate;
CREATE DATABASE english_mate;
python init_db.py
```

### Q2: Token过期怎么办？
使用Refresh Token获取新的Access Token：
```bash
curl -X POST http://localhost:8000/ai/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "your_refresh_token"}'
```

### Q3: 如何查看数据库内容？

**SQLite:**
```bash
sqlite3 english_mate.db
.tables
SELECT * FROM users;
```

**PostgreSQL:**
```bash
psql -U english_user -d english_mate
\dt
SELECT * FROM users;
```

### Q4: ChromaDB会受影响吗？
不会！ChromaDB继续独立工作，用于RAG知识检索，与用户认证系统完全分离。

---

## 📈 性能考虑

### 数据库优化
1. 使用连接池（PostgreSQL）
2. 添加适当的索引
3. 定期清理旧会话数据
4. 使用Redis缓存热点数据

### Token优化
1. 合理的过期时间
2. 实现Token刷新机制
3. 避免频繁重新登录

---

## 🎯 下一步计划

### 可选增强功能
- [ ] 邮箱验证
- [ ] 双因素认证（2FA）
- [ ] OAuth第三方登录
- [ ] 用户角色和权限
- [ ] Token黑名单（Redis）
- [ ] 登录日志和审计
- [ ] 速率限制
- [ ] 头像上传

---

## 📞 技术支持

如有问题，请查阅：
1. [DEPLOYMENT.md](DEPLOYMENT.md) - 完整部署指南
2. API文档：http://localhost:8000/docs
3. 测试脚本：`test_auth.py`

祝使用愉快！🎉
