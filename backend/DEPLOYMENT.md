# EnglishMateAI 后端部署指南

## 📋 目录结构

```
backend/
├── app/
│   ├── agents/          # AI代理
│   ├── api/v1/          # API路由
│   │   ├── auth.py      # 认证接口（新增）
│   │   ├── chat.py      # 聊天接口
│   │   └── chat_stream.py  # 流式聊天
│   ├── auth/            # 认证模块
│   │   ├── api_key_auth.py   # API Key认证（旧）
│   │   └── jwt_auth.py       # JWT认证（新）
│   ├── core/            # 核心功能
│   │   ├── database.py  # 数据库配置（新增）
│   │   ├── jwt.py       # JWT工具（新增）
│   │   ├── security.py  # 密码加密（新增）
│   │   ├── memory.py    # Redis记忆
│   │   └── rag.py       # RAG检索
│   ├── models/          # 数据模型（新增）
│   │   └── user.py      # 用户、会话、消息模型
│   ├── schemas/         # 数据验证
│   │   ├── auth.py      # 认证Schema（新增）
│   │   └── chat.py      # 聊天Schema
│   ├── services/        # 服务层（新增）
│   │   └── auth_service.py  # 认证服务
│   └── prompts/         # 提示词
├── chroma_db/           # 向量数据库（不变）
├── english_mate.db      # SQLite数据库（自动生成）
├── requirements.txt     # 依赖包
├── .env                 # 环境配置
└── main.py              # 入口文件
```

---

## 🔧 本地开发环境搭建

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# OpenAI API 配置
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus

# JWT 认证配置（重要：生产环境必须修改SECRET_KEY）
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 数据库配置（开发用SQLite，生产用PostgreSQL）
DATABASE_URL=sqlite:///./english_mate.db
```

### 3. 初始化数据库

```bash
python init_db.py
```

输出示例：
```
🗄️  开始初始化数据库...
✅ 数据库表创建成功！
📍 数据库位置: sqlite:///./english_mate.db

📋 已创建的表:
   - users
   - sessions
   - messages
```

### 4. 启动服务

```bash
python main.py
```

访问 http://localhost:8000/docs 查看API文档

---

## 🚀 生产环境部署

### 方案一：使用 PostgreSQL（推荐）

#### 1. 安装 PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

#### 2. 创建数据库和用户

```bash
sudo -u postgres psql

CREATE DATABASE english_mate;
CREATE USER english_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE english_mate TO english_user;
\q
```

#### 3. 更新 .env 配置

```env
# 数据库配置（生产环境）
DATABASE_URL=postgresql://english_user:your_secure_password@localhost:5432/english_mate

# JWT密钥（必须使用强随机字符串）
JWT_SECRET_KEY=$(openssl rand -hex 32)  # 生成随机密钥
```

#### 4. 安装 PostgreSQL 驱动

```bash
pip install psycopg2-binary
```

#### 5. 初始化数据库

```bash
python init_db.py
```

---

### 方案二：使用 Docker 部署

#### 1. 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/english_mate
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
      - OPENAI_MODEL=${OPENAI_MODEL}
    depends_on:
      - db
      - redis
    volumes:
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: english_mate
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### 3. 创建 .env 文件

```env
JWT_SECRET_KEY=your-super-secret-key
OPENAI_API_KEY=your-openai-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
```

#### 4. 启动服务

```bash
docker-compose up -d
```

---

## 🔐 安全建议

### 1. JWT密钥管理

**❌ 不要这样做：**
```env
JWT_SECRET_KEY=my-secret-key
```

**✅ 应该这样做：**
```bash
# 生成强随机密钥
python -c "import secrets; print(secrets.token_hex(32))"
```

将生成的密钥保存到 `.env` 文件，并设置正确的文件权限：
```bash
chmod 600 .env
```

### 2. 数据库安全

- 使用强密码
- 限制数据库访问IP
- 定期备份数据
- 启用SSL连接（生产环境）

### 3. CORS配置

生产环境不要使用 `*`，应该指定具体域名：

```env
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. HTTPS

生产环境必须使用HTTPS，可以通过Nginx反向代理实现。

---

## 📊 监控和维护

### 1. 查看日志

```bash
# 如果使用systemd
sudo journalctl -u english-mate-backend -f

# 如果使用docker
docker-compose logs -f backend
```

### 2. 数据库备份

**SQLite:**
```bash
cp english_mate.db english_mate_backup_$(date +%Y%m%d).db
```

**PostgreSQL:**
```bash
pg_dump -U english_user english_mate > backup_$(date +%Y%m%d).sql
```

### 3. 健康检查

```bash
curl http://localhost:8000/ai/
```

预期响应：
```json
{
  "status": "ok",
  "service": "FastAPI + LangChain AI 服务",
  "version": "1.0.0"
}
```

---

## 🔧 常见问题

### Q1: 数据库连接失败

**SQLite:**
- 检查文件路径是否正确
- 确保有写入权限

**PostgreSQL:**
```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 检查连接
psql -U english_user -d english_mate -h localhost
```

### Q2: Token验证失败

- 检查 `JWT_SECRET_KEY` 是否正确
- 确认Token未过期
- 检查Token格式是否为 `Bearer <token>`

### Q3: 导入错误

确保安装了所有依赖：
```bash
pip install -r requirements.txt
```

### Q4: ChromaDB和数据库冲突？

**不会冲突！** 
- ChromaDB：存储向量数据，用于RAG知识检索
- PostgreSQL/SQLite：存储用户数据、会话历史
- 两者职责分离，互不影响

---

## 📈 性能优化

### 1. 数据库连接池

PostgreSQL默认支持连接池，可以在 `database.py` 中配置：

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 连接池大小
    max_overflow=40,        # 最大溢出连接数
    pool_timeout=30,        # 超时时间
    pool_recycle=1800       # 连接回收时间（秒）
)
```

### 2. Redis缓存

继续使用Redis存储短期会话数据，减轻数据库压力。

### 3. 静态文件CDN

如果有头像等静态文件，建议使用CDN加速。

---

## 🎯 API使用示例

### 注册

```bash
curl -X POST http://localhost:8000/ai/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "123456",
    "full_name": "测试用户"
  }'
```

### 登录

```bash
curl -X POST http://localhost:8000/ai/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "123456"
  }'
```

响应：
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 调用聊天接口（需要认证）

```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{
    "question": "How to use present perfect tense?",
    "session_id": "my_session_1"
  }'
```

---

## ✅ 部署检查清单

- [ ] 修改 `JWT_SECRET_KEY` 为强随机字符串
- [ ] 配置正确的数据库连接
- [ ] 设置CORS允许的域名
- [ ] 配置OpenAI API密钥
- [ ] 初始化数据库表
- [ ] 测试注册、登录功能
- [ ] 测试聊天接口认证
- [ ] 配置HTTPS（生产环境）
- [ ] 设置日志轮转
- [ ] 配置数据库自动备份
- [ ] 设置监控告警

---

## 📞 技术支持

如有问题，请检查：
1. 日志文件
2. 数据库连接状态
3. 环境变量配置
4. API文档：http://localhost:8000/docs

祝部署顺利！🎉
