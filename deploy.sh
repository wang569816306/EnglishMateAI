#!/bin/bash
###############################################################################
# EnglishMateAI 一键部署脚本
# 适用于：Ubuntu 20.04/22.04, CentOS 7/8, Alibaba Cloud Linux
# 用法：bash deploy.sh [your-openai-api-key] [github-repo-url]
# 示例：bash deploy.sh sk-your-api-key https://github.com/username/EnglishMateAI.git
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
GITHUB_REPO="${2:-https://github.com/wang569816306/EnglishMateAI.git}"
PYTHON_CMD="python3"  # 默认 Python 命令
BRANCH="main"  # 默认分支

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
echo -e "${GREEN}📋 部署配置:${NC}"
echo -e "   GitHub 仓库: $GITHUB_REPO"
echo -e "   分支: $BRANCH"
echo -e "   部署目录: $PROJECT_DIR"
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
# 预检查：磁盘空间
###############################################################################
echo -e "${GREEN}🔍 预检查：磁盘空间...${NC}"

# 获取可用空间（KB）
AVAILABLE_SPACE=$(df -k /var/www | tail -1 | awk '{print $4}')
AVAILABLE_GB=$((AVAILABLE_SPACE / 1024 / 1024))

echo -e "${YELLOW}   可用空间: ${AVAILABLE_GB} GB${NC}"

# 至少需要 5GB
if [ $AVAILABLE_GB -lt 5 ]; then
    echo -e "${RED}❌ 磁盘空间不足！${NC}"
    echo -e "${YELLOW}   当前可用: ${AVAILABLE_GB} GB${NC}"
    echo -e "${YELLOW}   需要至少: 5 GB${NC}"
    echo -e ""
    echo -e "${YELLOW}解决方案:${NC}"
    echo -e "   1. 清理磁盘空间: rm -rf /tmp/* && pip cache purge && yum clean all"
    echo -e "   2. 扩展云盘容量（在阿里云控制台操作）"
    echo -e "   3. 删除不必要的大文件"
    exit 1
else
    echo -e "${GREEN}✅ 磁盘空间充足${NC}"
fi

echo ""

###############################################################################
# 步骤 0: 从 GitHub 克隆代码
###############################################################################
echo -e "${GREEN}[0/10] 从 GitHub 克隆代码...${NC}"

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠️  Git 未安装，正在安装...${NC}"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case $ID in
            ubuntu|debian)
                apt update -y && apt install -y git
                ;;
            centos|rhel|fedora|alinux)
                yum install -y git --nogpgcheck
                ;;
        esac
    fi
fi

# 如果目录已存在，先备份或删除
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  检测到旧项目目录，正在备份...${NC}"
    BACKUP_DIR="${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    mv $PROJECT_DIR $BACKUP_DIR
    echo -e "${GREEN}✅ 旧项目已备份到: $BACKUP_DIR${NC}"
fi

# 创建目录并克隆代码
echo -e "${YELLOW}正在从 GitHub 克隆代码...${NC}"
mkdir -p $(dirname $PROJECT_DIR)
cd $(dirname $PROJECT_DIR)

# 克隆代码（支持公开和私有仓库）
if git clone -b $BRANCH $GITHUB_REPO $PROJECT_DIR; then
    echo -e "${GREEN}✅ 代码克隆成功${NC}"
else
    echo -e "${RED}❌ 代码克隆失败${NC}"
    echo -e "${YELLOW}可能的原因:${NC}"
    echo -e "   1. GitHub 仓库地址错误"
    echo -e "   2. 网络连接问题（国内访问 GitHub 可能较慢）"
    echo -e "   3. 如果是私有仓库，需要使用 Token 认证"
    echo -e ""
    echo -e "${YELLOW}解决方案:${NC}"
    echo -e "   公开仓库: bash deploy.sh [api-key] https://github.com/username/repo.git"
    echo -e "   私有仓库: bash deploy.sh [api-key] https://TOKEN@github.com/username/repo.git"
    echo -e "   或者使用 Gitee 镜像仓库"
    exit 1
fi

cd $PROJECT_DIR

# 检查是否有前端静态文件，如果没有则提示
echo -e "${YELLOW}检查前端静态文件...${NC}"
if [ ! -f "$PROJECT_DIR/backend/static/index.html" ]; then
    echo -e "${YELLOW}⚠️  未检测到前端静态文件${NC}"
    echo -e "${YELLOW}   如果 GitHub 仓库中包含已构建的前端文件，请确保在 backend/static/ 目录${NC}"
    echo -e "${YELLOW}   否则需要在服务器上手动构建前端${NC}"
else
    echo -e "${GREEN}✅ 检测到前端静态文件${NC}"
fi

echo -e "${GREEN}✅ 代码克隆完成${NC}"
echo ""

###############################################################################
# 步骤 1: 安装系统依赖
###############################################################################
echo -e "${GREEN}[1/10] 安装系统依赖...${NC}"

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
        apt install -y python3 python3-pip python3-venv nodejs npm nginx git openssl curl wget trickle
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
        yum install -y nodejs npm nginx git openssl curl wget trickle --nogpgcheck
        
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
echo -e "${GREEN}[2/10] 创建项目目录...${NC}"

mkdir -p $PROJECT_DIR
# 优先使用 SERVICE_USER，如果失败则使用当前用户
chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR 2>/dev/null || chown -R $USER:$USER $PROJECT_DIR 2>/dev/null || true

echo -e "${GREEN}✅ 项目目录创建完成${NC}"
echo ""

###############################################################################
# 步骤 3: 配置后端环境
###############################################################################
echo -e "${GREEN}[3/10] 配置后端环境...${NC}"

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
echo -e "${GREEN}[4/10] 安装 Python 依赖并初始化数据库...${NC}"

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
# 如果安装了 trickle，可以使用它来限速
if command -v trickle &> /dev/null; then
    echo -e "${YELLOW}使用 trickle 限速下载...${NC}"
    trickle -d 5000 -u 1000 pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
else
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 安装依赖（使用国内镜像源加速，增加重试和超时避免 IO 过载）
echo -e "${YELLOW}正在安装 Python 依赖，这可能需要较长时间...${NC}"
echo -e "${YELLOW}提示：torch 包较大(900MB+)，请耐心等待${NC}"

# 检查是否安装 trickle（用于限速）
TRICKLE_CMD=""
if command -v trickle &> /dev/null; then
    TRICKLE_CMD="trickle -d 5000 -u 1000"
    echo -e "${GREEN}✅ 检测到 trickle，将限制下载速度为 5MB/s${NC}"
else
    echo -e "${YELLOW}⚠️  未检测到 trickle，将全速下载${NC}"
    echo -e "${YELLOW}   如需限速，请安装: yum install -y trickle${NC}"
fi

# 先安装小依赖包，最后安装 torch（减少瞬时 IO 压力）
echo -e "${GREEN}步骤 1: 安装基础依赖...${NC}"
$TRICKLE_CMD pip install fastapi uvicorn starlette pydantic pydantic-settings python-dotenv httpx python-multipart \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 2: 安装 LangChain 相关...${NC}"
$TRICKLE_CMD pip install langchain langchain-core langchain-community langchain-text-splitters \
    langchain-openai langchain-chroma langchain-huggingface \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 3: 安装向量数据库和 AI 模型...${NC}"
$TRICKLE_CMD pip install chromadb sentence-transformers transformers tokenizers huggingface-hub \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 4: 安装 PyTorch (最大包，约 900MB)...${NC}"
echo -e "${YELLOW}这一步最耗时，请耐心等待 30-60 分钟...${NC}"
$TRICKLE_CMD pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 5: 安装其他依赖...${NC}"
$TRICKLE_CMD pip install redis numpy scikit-learn scipy tenacity tiktoken pyyaml requests \
    PyJWT passlib python-jose sqlalchemy alembic psycopg2-binary aiosqlite \
    python-docx openpyxl xlrd openai-whisper yt-dlp \
    -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

echo -e "${GREEN}步骤 6: 安装部署工具...${NC}"
$TRICKLE_CMD pip install gunicorn docx2txt -i https://pypi.tuna.tsinghua.edu.cn/simple

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
echo -e "${GREEN}[5/10] 配置 Nginx...${NC}"

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
echo -e "${GREEN}[6/10] 创建系统服务...${NC}"

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
echo -e "${GREEN}[7/10] 配置防火墙...${NC}"

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
echo -e "${GREEN}[8/10] 创建备份脚本...${NC}"

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
echo -e "${GREEN}[9/10] 验证部署...${NC}"

# 等待服务启动
sleep 5

# 初始化检测结果
DEPLOY_SUCCESS=true

# 检查服务状态
echo -e "${YELLOW}🔍 检查服务状态...${NC}"
if systemctl is-active --quiet englishmate-backend; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC}"
else
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    echo -e "${YELLOW}   查看日志: journalctl -u englishmate-backend -f${NC}"
    DEPLOY_SUCCESS=false
fi

if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx 服务运行正常${NC}"
else
    echo -e "${RED}❌ Nginx 服务启动失败${NC}"
    DEPLOY_SUCCESS=false
fi

# 测试 API 连接
echo -e "${YELLOW}🔍 测试 API 连接...${NC}"
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API 健康检查通过${NC}"
else
    echo -e "${YELLOW}⚠️  API 健康检查失败，可能需要更多时间启动${NC}"
    echo -e "${YELLOW}   等待 10 秒后重试...${NC}"
    sleep 10
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API 健康检查通过（重试成功）${NC}"
    else
        echo -e "${RED}❌ API 健康检查仍然失败${NC}"
        echo -e "${YELLOW}   请检查: journalctl -u englishmate-backend -f${NC}"
        DEPLOY_SUCCESS=false
    fi
fi

# 检查前端文件
echo -e "${YELLOW}🔍 检查前端文件...${NC}"
if [ -f "$PROJECT_DIR/backend/static/index.html" ]; then
    echo -e "${GREEN}✅ 前端静态文件存在${NC}"
else
    echo -e "${RED}❌ 前端静态文件缺失${NC}"
    echo -e "${YELLOW}   请在服务器上构建前端: cd frontend && npm install && npx vite build && cp -r dist/* ../backend/static/${NC}"
    DEPLOY_SUCCESS=false
fi

# 检查数据库文件
echo -e "${YELLOW}🔍 检查数据库...${NC}"
if [ -f "$BACKEND_DIR/english_mate.db" ]; then
    echo -e "${GREEN}✅ 数据库文件存在${NC}"
else
    echo -e "${RED}❌ 数据库文件缺失${NC}"
    DEPLOY_SUCCESS=false
fi

# 检查 .env 配置文件
echo -e "${YELLOW}🔍 检查配置文件...${NC}"
if [ -f "$BACKEND_DIR/.env" ]; then
    echo -e "${GREEN}✅ 配置文件存在${NC}"
else
    echo -e "${RED}❌ 配置文件缺失${NC}"
    DEPLOY_SUCCESS=false
fi

# 测试 Nginx 代理
echo -e "${YELLOW}🔍 测试 Nginx 代理...${NC}"
if curl -s http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx 代理正常${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx 代理可能有问题${NC}"
    echo -e "${YELLOW}   检查 Nginx 配置: nginx -t${NC}"
fi

echo ""
if [ "$DEPLOY_SUCCESS" = true ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   ✅ 所有检查通过，部署成功！          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
else
    echo -e "${YELLOW}╔══════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║   ⚠️  部署完成，但部分检查未通过      ║${NC}"
    echo -e "${YELLOW}║   请查看上面的错误信息并手动修复      ║${NC}"
    echo -e "${YELLOW}╚══════════════════════════════════════════╝${NC}"
fi
echo ""

###############################################################################
# 步骤 10: 显示部署信息
###############################################################################
echo -e "${GREEN}[10/10] 生成部署报告...${NC}"

# 获取服务器 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo -e "${GREEN}✅ 部署报告生成完成${NC}"
echo ""

###############################################################################
# 部署完成
###############################################################################
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       🎉 部署完成！                    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📍 访问地址:${NC}"
echo -e "   http://$SERVER_IP"
echo ""
echo -e "${GREEN}📦 代码来源:${NC}"
echo -e "   GitHub: $GITHUB_REPO"
echo -e "   分支: $BRANCH"
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
