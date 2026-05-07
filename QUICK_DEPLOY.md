# EnglishMateAI 快速部署指南

## 🚀 一键部署（Docker Compose）

### 前置条件
```bash
# 检查 Docker 是否安装
docker --version
docker-compose --version
```

### 部署步骤

#### 1. 准备项目
```bash
# 克隆项目（如果是从Git仓库）
git clone <your-repository-url>
cd EnglishMateAI

# 或者直接上传项目文件到服务器
```

#### 2. 配置环境变量
```bash
# 复制环境变量模板
cp backend/.env.example backend/.env.production

# 编辑配置文件（必须修改以下内容）
vim backend/.env.production
```

**必须修改的配置：**
```env
# OpenAI API Key（替换为你的实际密钥）
OPENAI_API_KEY=sk-your-actual-api-key-here

# JWT密钥（生产环境必须使用强随机字符串）
JWT_SECRET_KEY=$(openssl rand -hex 32)

# 如果使用 PostgreSQL（推荐）
DATABASE_URL=postgresql://englishmate:your-strong-password@db:5432/english_mate
```

#### 3. 执行部署
```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

#### 4. 验证部署
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问应用
# 前端: http://your-server-ip
# 后端API: http://your-server-ip:8000
# API文档: http://your-server-ip:8000/docs
```

---

## 📦 手动部署（无 Docker）

### 后端部署

#### 1. 安装依赖
```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 Python 依赖
pip install --upgrade pip
pip install -r requirements.txt

# 安装系统依赖（Ubuntu/Debian）
sudo apt-get update
sudo apt-get install -y ffmpeg postgresql-client
```

#### 2. 配置数据库
```bash
# 使用 SQLite（开发/小规模）
# 无需额外配置，自动创建 english_mate.db

# 或使用 PostgreSQL（生产推荐）
sudo -u postgres psql
CREATE DATABASE english_mate;
CREATE USER englishmate WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE english_mate TO englishmate;
\q
```

#### 3. 初始化数据库
```bash
# 运行数据库迁移
python init_db.py

# 初始化推荐问题（可选）
python init_suggested_questions.py
```

#### 4. 启动服务
```bash
# 开发模式
python main.py

# 或使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 生产模式（使用 systemd）
sudo cp englishmate-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable englishmate-backend
sudo systemctl start englishmate-backend
```

### 前端部署

#### 1. 安装依赖
```bash
cd frontend

# 安装 Node.js 依赖
npm install
```

#### 2. 构建生产版本
```bash
npm run build
```

#### 3. 配置 Nginx
```bash
# 安装 Nginx
sudo apt-get install nginx

# 配置站点
sudo tee /etc/nginx/sites-available/englishmate << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/EnglishMateAI/frontend/dist;
    index index.html;

    # 处理 Vue Router 的 history 模式
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /ai/ {
        proxy_pass http://localhost:8000/ai/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # SSE 流式传输配置
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/englishmate /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

##  生产环境配置

### 1. 启用 HTTPS（Let's Encrypt）
```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 2. 配置防火墙
```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. 配置日志轮转
```bash
sudo tee /etc/logrotate.d/englishmate << 'EOF'
/var/log/englishmate/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data adm
}
EOF
```

### 4. 设置监控
```bash
# 安装监控工具
sudo apt-get install htop iotop nload

# 查看资源使用
htop        # CPU和内存
iotop       # 磁盘IO
nload       # 网络流量
```

---

##  常用运维命令

### Docker 方式
```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 重启服务
docker-compose restart backend

# 更新部署
git pull
docker-compose down
docker-compose up -d --build

# 备份数据
docker-compose exec db pg_dump -U user english_mate > backup_$(date +%Y%m%d).sql

# 进入容器
docker-compose exec backend bash
docker-compose exec db psql -U user -d english_mate
```

### 手动部署方式
```bash
# 查看服务状态
sudo systemctl status englishmate-backend

# 查看日志
sudo journalctl -u englishmate-backend -f

# 重启服务
sudo systemctl restart englishmate-backend

# 查看端口占用
sudo lsof -i :8000
sudo lsof -i :80

# 查看进程
ps aux | grep uvicorn
ps aux | grep nginx
```

---

##  故障排查

### 后端无法启动
```bash
# 检查端口占用
sudo lsof -i :8000

# 检查Python依赖
pip list | grep fastapi

# 检查数据库连接
python -c "from app.core.database import engine; print(engine.connect())"

# 查看详细日志
uvicorn main:app --log-level debug
```

### 前端无法访问
```bash
# 检查Nginx配置
sudo nginx -t

# 检查Nginx日志
sudo tail -f /var/log/nginx/error.log

# 检查构建产物
ls -la frontend/dist/
```

### AI 接口超时
```bash
# 检查 API Key 是否有效
curl -H "Authorization: Bearer your-api-key" https://api.openai.com/v1/models

# 检查网络连接
ping api.openai.com

# 增加超时时间
# 在 .env 中调整 TEMPERATURE 或检查网络代理
```

### 数据库连接失败
```bash
# 测试数据库连接
psql -h localhost -U user -d english_mate

# 检查数据库服务
sudo systemctl status postgresql

# 查看数据库日志
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## 📊 性能优化建议

### 1. 后端优化
```python
# 使用多个 worker 处理并发
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000

# 启用数据库连接池
# 在 database.py 中配置 pool_size 和 max_overflow
```

### 2. 前端优化
```bash
# 启用 gzip 压缩
# 在 Nginx 配置中添加：
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 启用浏览器缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 数据库优化
```sql
-- 添加索引
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_messages_session_id ON messages(session_id);

-- 定期清理旧数据
DELETE FROM sessions WHERE updated_at < NOW() - INTERVAL '90 days';
```

---

## 📞 技术支持

遇到问题？
1. 查看日志：`docker-compose logs -f` 或 `journalctl -u englishmate-backend`
2. 检查配置：`cat backend/.env.production`
3. 测试接口：访问 http://your-server-ip:8000/docs
4. 查看报告：阅读 `DEPLOYMENT_CHECKLIST.md`

---

**祝部署顺利！**
