#!/bin/bash
###############################################################################
# EnglishMateAI 一键部署脚本
# 适用于：Ubuntu 20.04/22.04, CentOS 7/8, Alibaba Cloud Linux
# 用法：bash deploy.sh [your-openai-api-key]
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_DIR="/var/www/englishmate"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
API_KEY="${1:-}"
PYTHON_CMD="python3"  # 默认 Python 命令

# 检测系统用户（用于 systemd 服务）
if id -u www-data &>/dev/null; then
    SERVICE_USER="www-data"
elif id -u nginx &>/dev/null; then
    SERVICE_USER="nginx"
else
    SERVICE_USER="root"
fi

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 EnglishMateAI 一键部署脚本        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  重要提示：${NC}"
echo -e "${YELLOW}   在运行此脚本前，请先手动构建前端代码并放到后端目录${NC}"
echo -e "${YELLOW}   执行命令：${NC}"
echo -e "${YELLOW}     cd frontend && npm install && npx vite build${NC}"
echo -e "${YELLOW}     cp -r dist/* ../backend/static/${NC}"
echo ""

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 获取 API Key
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}⚠️  请输入你的 OpenAI API Key:${NC}"
    read -s API_KEY
    echo ""
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ API Key 不能为空${NC}"
    exit 1
fi

###############################################################################
# 步骤 1: 安装系统依赖
###############################################################################
echo -e "${GREEN}[1/9] 安装系统依赖...${NC}"

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo -e "${RED}❌ 无法检测操作系统${NC}"
    exit 1
fi

case $OS in
    ubuntu|debian)
        apt update -y
        apt install -y python3 python3-pip python3-venv nodejs npm nginx git openssl curl wget
        # 确定使用的 Python 命令
        if command -v python3.11 &>/dev/null; then
            PYTHON_CMD="python3.11"
        elif command -v python3.10 &>/dev/null; then
            PYTHON_CMD="python3.10"
        elif command -v python3.9 &>/dev/null; then
            PYTHON_CMD="python3.9"
        elif command -v python3.8 &>/dev/null; then
            PYTHON_CMD="python3.8"
        elif command -v python3 &>/dev/null; then
            PYTHON_CMD="python3"
        else
            echo -e "${RED}❌ 未找到任何 Python 版本${NC}"
            exit 1
        fi
        
        # 检查 Python 版本
        PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        echo -e "${GREEN}✅ 使用 Python $PYTHON_VERSION ($PYTHON_CMD)${NC}"
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            echo -e "${RED}❌ Python $PYTHON_VERSION 版本太低，需要 3.8+${NC}"
            echo -e "${YELLOW}请手动安装 Python 3.8 或更高版本${NC}"
            exit 1
        fi
        ;;
    centos|rhel|fedora|alinux)
        yum update -y --nogpgcheck
        
        # 先尝试安装高版本 Python
        PYTHON_INSTALLED=false
        for pyver in python3.11 python39 python38; do
            if yum install -y $pyver $pyver-pip $pyver-devel --nogpgcheck 2>/dev/null; then
                echo -e "${GREEN}✅ 已安装 $pyver${NC}"
                PYTHON_INSTALLED=true
                break
            fi
        done
        
        # 如果没安装到高版本，再安装默认 python3
        if [ "$PYTHON_INSTALLED" = false ]; then
            echo -e "${YELLOW}⚠️  未找到 Python 3.8+，安装默认 python3...${NC}"
            yum install -y python3 python3-pip python3-devel --nogpgcheck
        fi
        
        # 安装其他依赖
        yum install -y nodejs npm nginx git openssl curl wget --nogpgcheck
        
        # 确定使用的 Python 命令
        if command -v python3.11 &>/dev/null; then
            PYTHON_CMD="python3.11"
        elif command -v python3.9 &>/dev/null; then
            PYTHON_CMD="python3.9"
        elif command -v python3.8 &>/dev/null; then
            PYTHON_CMD="python3.8"
        elif command -v python3 &>/dev/null; then
            PYTHON_CMD="python3"
        else
            echo -e "${RED}❌ 未找到任何 Python 版本${NC}"
            exit 1
        fi
        
        # 检查 Python 版本
        PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        echo -e "${GREEN}✅ 使用 Python $PYTHON_VERSION ($PYTHON_CMD)${NC}"
        
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
            echo -e "${RED}❌ Python $PYTHON_VERSION 版本太低，需要 3.8+${NC}"
            echo -e "${YELLOW}请手动安装 Python 3.8 或更高版本${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ 不支持的操作系统: $OS${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ 系统依赖安装完成${NC}"
echo ""

###############################################################################
# 步骤 2: 创建项目目录并设置权限
###############################################################################
echo -e "${GREEN}[2/9] 创建项目目录...${NC}"

mkdir -p $PROJECT_DIR
# 优先使用 SERVICE_USER，如果失败则使用当前用户
chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR 2>/dev/null || chown -R $USER:$USER $PROJECT_DIR 2>/dev/null || true

echo -e "${GREEN}✅ 项目目录创建完成${NC}"
echo ""

###############################################################################
# 步骤 3: 配置后端环境
###############################################################################
echo -e "${GREEN}[3/9] 配置后端环境...${NC}"

# 生成 JWT 密钥
JWT_SECRET=$(openssl rand -hex 32)

# 在后端目录创建环境变量文件
cd $BACKEND_DIR
cat > .env << EOF
# OpenAI API 配置
OPENAI_API_KEY=$API_KEY
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus

# JWT 配置
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 数据库配置
DATABASE_URL=sqlite:///./english_mate.db

# CORS 配置
CORS_ORIGINS=*

# API Key 认证（关闭，使用 JWT 认证）
API_KEY_ENABLED=false

# 服务配置
SERVICE_NAME='EnglishMateAI'
SERVICE_VERSION='1.0.0'
EOF

# 保护敏感文件
chmod 600 .env

echo -e "${GREEN}✅ 后端环境配置完成${NC}"
echo ""

###############################################################################
# 步骤 4: 安装 Python 依赖并初始化
###############################################################################
echo -e "${GREEN}[4/9] 安装 Python 依赖并初始化数据库...${NC}"

# 已在 backend 目录下

# 删除旧的虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  检测到旧虚拟环境，正在清理...${NC}"
    rm -rf venv
fi

# 创建虚拟环境（使用正确的 Python 版本）
${PYTHON_CMD:-python3} -m venv venv
source venv/bin/activate

# 升级 pip（使用国内镜像源，限速避免 IO 过载）
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖（使用国内镜像源加速，增加重试和超时避免 IO 过载）
echo -e "${YELLOW}正在安装 Python 依赖，这可能需要较长时间...${NC}"
echo -e "${YELLOW}提示：torch 包较大(900MB+)，请耐心等待${NC}"

# 先安装小依赖包，最后安装 torch（减少瞬时 IO 压力）
echo -e "${GREEN}步骤 1: 安装基础依赖...${NC}"
pip install fastapi uvicorn starlette pydantic pydantic-settings python-dotenv httpx python-multipart \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 2: 安装 LangChain 相关...${NC}"
pip install langchain langchain-core langchain-community langchain-text-splitters \
    langchain-openai langchain-chroma langchain-huggingface \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 3: 安装向量数据库和 AI 模型...${NC}"
pip install chromadb sentence-transformers transformers tokenizers huggingface-hub \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 4: 安装 PyTorch (最大包，约 900MB)...${NC}"
echo -e "${YELLOW}这一步最耗时，请耐心等待 30-60 分钟...${NC}"
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 5: 安装其他依赖...${NC}"
pip install redis numpy scikit-learn scipy tenacity tiktoken pyyaml requests \
    PyJWT passlib python-jose sqlalchemy alembic psycopg2-binary aiosqlite \
    python-docx openpyxl xlrd openai-whisper yt-dlp \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 6: 安装部署工具...${NC}"
pip install gunicorn docx2txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 初始化数据库
$PYTHON_CMD init_db.py

# 创建默认用户
$PYTHON_CMD create_default_user.py 2>/dev/null || echo "跳过用户创建"

# 初始化推荐问题
$PYTHON_CMD init_suggested_questions.py 2>/dev/null || echo "跳过推荐问题初始化"

echo -e "${GREEN}✅ Python 环境配置完成${NC}"
echo ""

###############################################################################
# 步骤 5: 配置 Nginx
###############################################################################
echo -e "${GREEN}[5/9] 配置 Nginx...${NC}"

# 检查 Nginx 配置目录
if [ -d "/etc/nginx/conf.d" ]; then
    NGINX_CONF_DIR="/etc/nginx/conf.d"
    NGINX_CONF_FILE="$NGINX_CONF_DIR/englishmate.conf"
elif [ -d "/etc/nginx/sites-available" ]; then
    NGINX_CONF_DIR="/etc/nginx/sites-available"
    NGINX_CONF_FILE="$NGINX_CONF_DIR/englishmate"
else
    echo -e "${RED}❌ 未找到 Nginx 配置目录${NC}"
    exit 1
fi

# 创建 Nginx 配置文件
cat > $NGINX_CONF_FILE << 'EOF'
server {
    listen 80;
    server_name _;
    
    # 前端静态文件
    location / {
        root /var/www/englishmate/backend/static;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # 后端 API 代理
    location /ai/ {
        proxy_pass http://127.0.0.1:8000;
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
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 日志
    access_log /var/log/nginx/englishmate_access.log;
    error_log /var/log/nginx/englishmate_error.log;
}
EOF

# 启用站点
if [ "$NGINX_CONF_DIR" = "/etc/nginx/sites-available" ]; then
    ln -sf $NGINX_CONF_FILE /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
fi

# 测试并重启 Nginx
nginx -t && systemctl restart nginx && systemctl enable nginx || {
    echo -e "${YELLOW}⚠️  Nginx 配置失败，请手动检查${NC}"
}

echo -e "${GREEN}✅ Nginx 配置完成${NC}"
echo ""

###############################################################################
# 步骤 6: 创建 systemd 服务
###############################################################################
echo -e "${GREEN}[6/9] 创建系统服务...${NC}"

cat > /etc/systemd/system/englishmate-backend.service << EOF
[Unit]
Description=EnglishMateAI Backend Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/gunicorn main:app \\
    --workers 2 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 127.0.0.1:8000 \\
    --timeout 120 \\
    --keep-alive 5 \\
    --access-logfile - \\
    --error-logfile -

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
systemctl daemon-reload

# 启动服务
systemctl start englishmate-backend
systemctl enable englishmate-backend

echo -e "${GREEN}✅ 系统服务创建完成${NC}"
echo ""

###############################################################################
# 步骤 7: 配置防火墙
###############################################################################
echo -e "${GREEN}[7/9] 配置防火墙...${NC}"

# Ubuntu UFW
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo -e "${GREEN}✅ UFW 防火墙配置完成${NC}"
# CentOS firewalld
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo -e "${GREEN}✅ Firewalld 防火墙配置完成${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到防火墙，请手动配置${NC}"
fi

echo ""

###############################################################################
# 步骤 8: 创建备份脚本
###############################################################################
echo -e "${GREEN}[8/9] 创建备份脚本...${NC}"

mkdir -p /backup/englishmate

cat > /usr/local/bin/englishmate-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/englishmate"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/var/www/englishmate/backend/english_mate.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/english_mate_$DATE.db"

# 保留最近30天的备份
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "备份完成: $BACKUP_DIR/english_mate_$DATE.db"
EOF

chmod +x /usr/local/bin/englishmate-backup.sh

# 设置每日备份
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/englishmate-backup.sh >> /var/log/englishmate-backup.log 2>&1") | crontab -

echo -e "${GREEN}✅ 备份脚本创建完成${NC}"
echo ""

###############################################################################
# 步骤 9: 验证部署
###############################################################################
echo -e "${GREEN}[9/9] 验证部署...${NC}"

# 等待服务启动
sleep 5

# 检查服务状态
if systemctl is-active --quiet englishmate-backend; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败，请检查日志: journalctl -u englishmate-backend -f${NC}"
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx 服务运行正常${NC}"
else
    echo -e "${RED}❌ Nginx 服务启动失败${NC}"
fi

# 测试 API 连接
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 健康检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  API 健康检查失败，可能需要更多时间启动${NC}"
fi

echo ""

###############################################################################
# 部署完成
###############################################################################
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🎉 部署完成！                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# 获取服务器 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo -e "${GREEN}📍 访问地址:${NC}"
echo -e "   http://$SERVER_IP"
echo ""
echo -e "${GREEN}🔑 默认管理员账号:${NC}"
echo -e "   用户名: admin"
echo -e "   密码: admin123"
echo ""
echo -e "${GREEN}📊 服务状态:${NC}"
echo -e "   后端: $(systemctl is-active englishmate-backend)"
echo -e "   Nginx: $(systemctl is-active nginx)"
echo ""
echo -e "${GREEN}📝 常用命令:${NC}"
echo -e "   查看日志: journalctl -u englishmate-backend -f"
echo -e "   重启服务: systemctl restart englishmate-backend"
echo -e "   手动备份: /usr/local/bin/englishmate-backup.sh"
echo ""
echo -e "${YELLOW}⚠️  重要提示:${NC}"
echo -e "   1. 请立即修改默认密码"
echo -e "   2. 建议配置 HTTPS（使用 certbot）"
echo -e "   3. 定期检查备份文件"
echo ""
echo -e "${GREEN}✨ 祝你使用愉快！${NC}"
