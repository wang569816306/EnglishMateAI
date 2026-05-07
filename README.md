# EnglishMateAI 项目启动指南

## 📋 前置要求

在开始之前，请确保你的系统已安装以下软件：

- **Python 3.11+** - 后端运行环境
- **Node.js 18+** - 前端运行环境
- **npm** 或 **pnpm** - Node.js 包管理器
- **ffmpeg** (可选) - 视频格式转换支持

---

## 🚀 快速启动（3步搞定）

### 第一步：安装后端依赖并启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key

# 初始化数据库
python3 init_db.py

# 启动后端服务
python3 main.py
```

后端服务将在 `http://localhost:8000` 启动。

---

### 第二步：安装前端依赖并启动

打开**新的终端窗口**，执行：

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选，已有默认配置）
cp .env.example .env

# 启动前端开发服务器
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

---

### 第三步：访问应用

在浏览器中打开：**http://localhost:5173**

🎉 恭喜！项目已成功启动！

---

## 📝 详细配置说明

### 后端配置（backend/.env）

必须配置的项：

```env
# OpenAI API 配置（必填）
OPENAI_API_KEY='your-api-key-here'
OPENAI_BASE_URL='https://dashscope.aliyuncs.com/compatible-mode/v1'
OPENAI_MODEL='qwen-plus'

# JWT 密钥（生产环境请修改）
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
```

可选配置：

```env
# 数据库配置（默认使用 SQLite，无需额外配置）
DATABASE_URL=sqlite:///./english_mate.db

# CORS 配置（默认允许所有来源）
CORS_ORIGINS='*'

# 请求体大小限制（默认 1MB）
MAX_REQUEST_SIZE=1048576
```

### 前端配置（frontend/.env）

通常无需修改，默认配置即可：

```env
VITE_API_BASE_URL=http://localhost:8000/ai
```

如果需要从其他设备访问（如手机、平板），改为实际IP：

```env
VITE_API_BASE_URL=http://192.168.x.x:8000/ai
```

---

## 🔧 常见问题

### 1. 端口被占用

**后端端口 8000 被占用：**
```bash
# 查找并杀死占用端口的进程
lsof -ti:8000 | xargs kill -9
```

**前端端口 5173 被占用：**
```bash
# 查找并杀死占用端口的进程
lsof -ti:5173 | xargs kill -9
```

### 2. Python 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 如果某些包安装失败，尝试单独安装
pip install <package-name>

# macOS M1/M2 芯片可能需要安装额外依赖
brew install ffmpeg
```

### 3. Node.js 依赖安装失败

```bash
# 清除缓存后重新安装
rm -rf node_modules package-lock.json
npm install

# 或使用淘宝镜像加速
npm install --registry=https://registry.npmmirror.com
```

### 4. 数据库初始化失败

```bash
# 删除旧数据库文件后重新初始化
cd backend
rm english_mate.db
python3 init_db.py
```

### 5. B站视频下载失败

确保 yt-dlp 是最新版本：

```bash
cd backend
pip install --upgrade yt-dlp
```

### 6. 前端无法连接后端

检查以下几点：

1. 后端服务是否正常运行：访问 http://localhost:8000/ai/
2. 前端配置是否正确：检查 `frontend/.env` 中的 `VITE_API_BASE_URL`
3. 浏览器控制台是否有 CORS 错误

---

## 📦 项目结构

```
EnglishMateAI/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   ├── main.py          # 入口文件
│   ├── requirements.txt # Python 依赖
│   ├── .env             # 环境变量配置
│   └── english_mate.db  # SQLite 数据库
│
├── frontend/            # 前端服务
│   ├── src/            # 源代码
│   ├── package.json    # Node.js 依赖
│   └── .env            # 环境变量配置
│
└── README.md           # 本文件
```

---

## 🛠️ 开发技巧

### 后端热重载

后端使用 `uvicorn` 的 `reload=True` 模式，修改代码后会自动重启。

### 前端热重载

前端使用 Vite 开发服务器，修改代码后会立即更新浏览器。

### 查看 API 文档

后端启动后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 停止服务

**停止后端：** 在后端终端按 `Ctrl+C`

**停止前端：** 在前端终端按 `Ctrl+C`

---

## 📞 需要帮助？

如果遇到问题：

1. 检查终端输出的错误信息
2. 查看本文档的"常见问题"部分
3. 确认所有依赖都已正确安装
4. 确认环境变量配置正确

---

## ✨ 功能特性

- ✅ AI 英语对话练习
- ✅ 视频下载与解析（支持 B站、YouTube 等）
- ✅ 口语训练与发音评分
- ✅ 场景化对话生成
- ✅ 文档上传与分析
- ✅ AI 智能总结
- ✅ 用户认证与会话管理

---

**祝你使用愉快！** 🎊
