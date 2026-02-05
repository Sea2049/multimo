#!/bin/bash
# ===========================================
# Multimo 服务器端部署脚本
# 在阿里云 ECS 上执行
# 用法: sudo bash server-deploy.sh [环境]
# ===========================================

set -e

# 配置
PROJECT_DIR="/opt/multimo"
REPO_URL="https://github.com/your-username/multimo.git"  # 修改为你的仓库地址
BRANCH="main"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

ENV=${1:-all}

echo ""
echo "=========================================="
echo "    Multimo 服务器部署脚本"
echo "=========================================="
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 sudo 运行此脚本"
    exit 1
fi

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装！请先运行 init-ecs.sh"
    exit 1
fi

# 进入项目目录
cd $PROJECT_DIR

# 检查是否已克隆代码
if [ ! -f "docker-compose.prod.yml" ]; then
    log_info "首次部署，克隆代码..."
    
    # 如果目录不为空，先备份
    if [ "$(ls -A $PROJECT_DIR)" ]; then
        log_warning "项目目录不为空，备份现有文件..."
        mkdir -p /opt/multimo-backup
        mv $PROJECT_DIR/* /opt/multimo-backup/ 2>/dev/null || true
    fi
    
    git clone $REPO_URL .
    git checkout $BRANCH
else
    log_info "更新代码..."
    git fetch origin
    git reset --hard origin/$BRANCH
fi

# 检查证书文件
log_info "检查 SSL 证书..."
CERT_DIR="$PROJECT_DIR/deploy/cloudflare/certs"

if [ ! -f "$CERT_DIR/origin.pem" ] || [ ! -f "$CERT_DIR/origin.key" ]; then
    log_error "未找到 SSL 证书！"
    echo ""
    echo "请将 Cloudflare Origin Certificate 放置到:"
    echo "  $CERT_DIR/origin.pem"
    echo "  $CERT_DIR/origin.key"
    echo ""
    echo "或者从本地复制:"
    echo "  scp origin.pem origin.key root@<ECS_IP>:$CERT_DIR/"
    exit 1
fi

# 设置证书权限
chmod 600 $CERT_DIR/origin.pem $CERT_DIR/origin.key
log_success "SSL 证书检查通过"

# 检查环境变量文件
check_env_file() {
    local env_file=$1
    local example_file=$2
    
    if [ ! -f "$env_file" ]; then
        if [ -f "$example_file" ]; then
            log_warning "$env_file 不存在，从模板创建..."
            cp "$example_file" "$env_file"
            log_error "请编辑 $env_file 配置环境变量，然后重新运行此脚本"
            exit 1
        else
            log_error "$env_file 和 $example_file 都不存在！"
            exit 1
        fi
    fi
}

# 根据环境部署
case $ENV in
    prod|production)
        check_env_file ".env.production" ".env.production.example"
        log_info "部署 Production 环境..."
        bash deploy.sh prod
        ;;
    staging|test)
        check_env_file ".env.staging" ".env.staging.example"
        log_info "部署 Staging 环境..."
        bash deploy.sh staging
        ;;
    all)
        check_env_file ".env.production" ".env.production.example"
        check_env_file ".env.staging" ".env.staging.example"
        log_info "部署所有环境..."
        bash deploy.sh all
        ;;
    *)
        echo "用法: sudo bash server-deploy.sh [prod|staging|all]"
        exit 1
        ;;
esac

# 显示状态
echo ""
log_info "部署状态:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
log_success "部署完成！"
echo ""
echo "访问地址:"
echo "  Production: https://multimo.sea-ming.com"
echo "  Staging:    https://test.sea-ming.com"
