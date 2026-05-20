#!/bin/bash
###############################################################################
# EnglishMateAI 一键部署脚本
# 适用于：Ubuntu 20.04/22.04, CentOS 7/8
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

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   🚀 EnglishMateAI 一键部署脚本        ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}⚠️  重要提示：${NC}"
echo -e "${YELLOW}   在运行此脚本前，请先手动构建前端代码并放到后端目录${NC}"
echo -e "${YELLOW}   执行命令：${NC}"
echo -e "${YELLOW}     cd frontend && npm run build${NC}"
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
echo -e "${GREEN}[1/7] 安装系统依赖...${NC}"

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
        ;;
    centos|rhel|fedora)
        yum update -y
        yum install -y python3 python3-pip python3-devel nodejs npm nginx git openssl curl wget
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
echo -e "${GREEN}[1/5] 创建项目目录...${NC}"

mkdir -p $PROJECT_DIR
chown -R $USER:$USER $PROJECT_DIR

echo -e "${GREEN}✅ 项目目录创建完成${NC}"
echo ""

###############################################################################
# 步骤 3: 配置后端环境
###############################################################################
echo -e "${GREEN}[2/5] 配置后端环境...${NC}"

# 生成 JWT 密钥
JWT_SECRET=$(openssl rand -hex 32)

# 创建环境变量文件
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
echo -e "${GREEN}[3/5] 安装 Python 依赖并初始化数据库...${NC}"

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip --quiet

# 安装依赖
pip install -r requirements.txt --quiet
pip install gunicorn docx2txt --quiet

# 初始化数据库
python3 init_db.py

# 创建默认用户
python3 create_default_user.py 2>/dev/null || echo "跳过用户创建"

# 初始化推荐问题
python3 init_suggested_questions.py 2>/dev/null || echo "跳过推荐问题初始化"

echo -e "${GREEN}✅ Python 环境配置完成${NC}"
echo ""

###############################################################################
# 步骤 5: 配置 Nginx
###############################################################################
echo -e "${GREEN}[4/5] 配置 Nginx...${NC}"

# 创建 Nginx 配置文件
cat > /etc/nginx/sites-available/englishmate << 'EOF'
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
ln -sf /etc/nginx/sites-available/englishmate /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试并重启 Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}✅ Nginx 配置完成${NC}"
echo ""

###############################################################################
# 步骤 8: 创建 systemd 服务
###############################################################################
echo -e "${GREEN}创建系统服务...${NC}"

cat > /etc/systemd/system/englishmate-backend.service << EOF
[Unit]
Description=EnglishMateAI Backend Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
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
# 步骤 9: 配置防火墙
###############################################################################
echo -e "${GREEN}配置防火墙...${NC}"

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
# 步骤 10: 创建备份脚本
###############################################################################
echo -e "${GREEN}创建备份脚本...${NC}"

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
