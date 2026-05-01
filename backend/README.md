# EnglishMateAI - AI 英语学习助手

一个基于 FastAPI + LangChain 的智能英语学习平台，提供口语练习、语法纠正、翻译、单词讲解等功能。

## 🚀 快速开始

### 前置要求

- Python 3.11+
- Redis（用于存储对话历史）
- pip（Python 包管理器）

---

## 📋 安装步骤

### 1️⃣ 安装 Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**验证 Redis 是否运行:**
```bash
redis-cli ping
# 应该返回: PONG
```

---

### 2️⃣ 克隆项目并进入后端目录

```bash
cd /Applications/Ai/EnglishMateAI/backend
```

---

### 3️⃣ 创建虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

---

### 4️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

> ⏱️ 首次安装可能需要几分钟，因为需要下载 PyTorch 和 HuggingFace 相关模型库

---

### 5️⃣ 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
vim .env  # 或使用你喜欢的编辑器
```

**必需配置项：**

```env
# OpenAI API 配置（使用阿里云通义千问示例）
OPENAI_API_KEY='your-api-key-here'
OPENAI_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1'
OPENAI_MODEL='qwen-plus'

# 如果使用 OpenAI 官方 API：
# OPENAI_BASE_URL='https://api.openai.com/v1'
# OPENAI_MODEL='gpt-3.5-turbo'
```

**可选配置项：**

```env
# 服务配置
SERVICE_NAME='FastAPI + LangChain AI 服务'
SERVICE_VERSION='1.0.0'
TEMPERATURE=0.7

# CORS 配置
CORS_ORIGINS='*'

# 请求体大小限制（默认 1MB）
MAX_REQUEST_SIZE=1048576

# API Key 认证（开发环境建议关闭）
API_KEY_ENABLED=false
API_KEYS=test-key-12345,admin-key-67890
```

---

### 6️⃣ 启动服务

```bash
python3 main.py
```

成功启动后会看到：

```
╔══════════════════════════════════════════╗
║                                          ║
║   🚀  Fast-AI Service                   ║
║   FastAPI + LangChain AI Platform       ║
║                                          ║
╚══════════════════════════════════════════╝

📍 服务地址: http://localhost:8000
📊 API文档: http://localhost:8000/docs
🔖 版本信息: FastAPI + LangChain AI 服务 v1.0.0
==================================================

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

---

## 🧪 测试服务

### 方法 1：浏览器访问 API 文档

打开浏览器访问：http://localhost:8000/docs

这是 Swagger UI 界面，可以直接测试所有 API 接口。

---

### 方法 2：使用 curl 测试

**健康检查：**
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

**聊天接口测试：**
```bash
curl -X POST "http://localhost:8000/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Hello, how are you?",
    "session_id": "test-session-001"
  }'
```

> 💡 如果启用了 API Key 认证，需要添加请求头：`-H "X-API-Key: test-key-12345"`

---

## 📁 项目结构

```
backend/
├── app/
│   ├── agents/              # AI Agent 实现
│   │   ├── chat_agent.py           # 普通聊天 Agent
│   │   └── chat_agent_stream.py    # 流式聊天 Agent
│   ├── api/                 # API 路由
│   │   └── v1/
│   │       ├── chat.py             # 聊天接口
│   │       ├── chat_stream.py      # 流式聊天接口
│   │       └── health.py           # 健康检查
│   ├── auth/                # 认证模块
│   │   └── api_key_auth.py         # API Key 认证
│   ├── core/                # 核心功能
│   │   ├── middlewares/            # 中间件
│   │   ├── memory.py               # 对话记忆（Redis）
│   │   ├── rag.py                  # RAG 知识库检索
│   │   ├── redis.py                # Redis 客户端
│   │   └── prompt_loader.py        # Prompt 加载器
│   ├── prompts/             # Prompt 模板
│   │   └── english_teacher.json    # 英语老师 Prompt
│   ├── rag/                 # 知识库文件
│   │   └── english_knowledge.txt   # 英语知识文本
│   ├── schemas/             # 数据模型
│   └── settings.py          # 配置管理
├── chroma_db/               # 向量数据库（自动生成）
├── .env                     # 环境变量配置
├── .env.example             # 环境变量示例
├── main.py                  # 应用入口
├── requirements.txt         # Python 依赖
└── README.md                # 项目说明
```

---

## 🔧 常见问题

### 1. HuggingFace 模型下载超时

**问题：** 启动时卡在下载 `all-MiniLM-L6-v2` 模型

**解决方案：** 项目已配置国内镜像源 `hf-mirror.com`，如果仍然超时：

```bash
# 手动预下载模型
export HF_ENDPOINT=https://hf-mirror.com
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

### 2. Redis 连接失败

**问题：** `ConnectionError: Error connecting to localhost:6379`

**解决方案：**
```bash
# 检查 Redis 是否运行
redis-cli ping

# 如果没有运行，启动 Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis-server
```

---

### 3. 端口被占用

**问题：** `Address already in use`

**解决方案：**
```bash
# 查找占用 8000 端口的进程
lsof -ti:8000

# 杀死进程
lsof -ti:8000 | xargs kill -9

# 或者修改 main.py 中的端口号
```

---

### 4. 依赖安装失败

**问题：** 某些包安装失败

**解决方案：**
```bash
# 升级 pip
pip install --upgrade pip

# 清理缓存后重新安装
pip cache purge
pip install -r requirements.txt

# 如果某个包单独失败，尝试单独安装
pip install <package-name>
```

---

### 5. API Key 认证问题

**问题：** 返回 401 Unauthorized

**解决方案：**

检查 `.env` 配置：
```env
# 开发环境建议关闭认证
API_KEY_ENABLED=false

# 如果启用，确保使用正确的 API Key
API_KEYS=test-key-12345,admin-key-67890
```

请求时添加 Header：
```bash
curl -H "X-API-Key: test-key-12345" http://localhost:8000/ai/
```

---

## 🛠️ 开发指南

### 热重载模式

服务默认以热重载模式运行，修改代码后会自动重启：

```bash
python3 main.py
```

看到 `Will watch for changes` 表示热重载已启用。

---

### 查看日志

日志会直接输出到控制台，格式为：
```
2024-01-01 12:00:00 | INFO     | fast-ai | chat_agent.py:48 | 收到聊天请求: Hello...
```

---

### 停止服务

在终端按 `Ctrl+C` 即可停止服务。

---

## 📚 API 接口说明

### 基础路径
```
http://localhost:8000/ai
```

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/chat` | POST | 普通聊天（等待完整回复） |
| `/chat/stream` | POST | 流式聊天（SSE 实时推送） |

详细接口文档请访问：http://localhost:8000/docs

---

## 🔐 安全建议

生产环境部署时：

1. ✅ 启用 API Key 认证：`API_KEY_ENABLED=true`
2. ✅ 使用强 API Keys，不要使用示例密钥
3. ✅ 配置合适的 CORS 白名单，不要使用 `*`
4. ✅ 设置合理的请求体大小限制
5. ✅ 使用 HTTPS
6. ✅ 定期更新依赖包

---

## 📄 许可证

本项目仅供学习和个人使用。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📞 支持

如有问题，请提交 Issue 或联系项目维护者。

---

**祝你使用愉快！🎉**
