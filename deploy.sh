#!/bin/bash
# ===========================================
# Multimo 部署脚本
# 用法: 
#   ./deploy.sh prod     - 部署 Production 环境
#   ./deploy.sh staging  - 部署 Staging 环境
#   ./deploy.sh all      - 部署所有环境 (默认)
# ===========================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# 获取环境参数
ENV=${1:-all}

echo ""
echo "=========================================="
echo "       Multimo 部署脚本"
echo "=========================================="
echo ""

# 检查证书文件
check_certificates() {
    log_info "检查 SSL 证书..."
    if [ ! -f "deploy/cloudflare/certs/origin.pem" ] || [ ! -f "deploy/cloudflare/certs/origin.key" ]; then
        log_error "未找到 SSL 证书文件！"
        echo "请将 Cloudflare Origin Certificate 放置到:"
        echo "  - deploy/cloudflare/certs/origin.pem"
        echo "  - deploy/cloudflare/certs/origin.key"
        exit 1
    fi
    log_success "SSL 证书检查通过"
}

# 部署 Production 环境
deploy_prod() {
    log_info "开始部署 Production 环境..."
    
    # 检查 .env.production 文件
    if [ ! -f ".env.production" ]; then
        log_error "未找到 .env.production 文件！"
        echo "请先复制 .env.production.example 为 .env.production 并配置环境变量。"
        exit 1
    fi
    
    # 创建数据目录
    mkdir -p data/prod/uploads data/prod/logs
    
    # 拉取最新代码 (如果是 git 仓库)
    if [ -d .git ]; then
        log_info "拉取最新代码..."
        git pull || log_warning "Git pull 失败，继续使用本地代码"
    fi
    
    # 构建并启动容器
    log_info "构建并启动 Production 容器..."
    docker compose -f docker-compose.prod.yml up -d --build
    
    if [ $? -eq 0 ]; then
        log_success "Production 环境部署成功！"
        echo "访问地址: https://multimo.sea-ming.com"
    else
        log_error "Production 部署失败，请检查 Docker 日志"
        exit 1
    fi
}

# 部署 Staging 环境
deploy_staging() {
    log_info "开始部署 Staging 环境..."
    
    # 检查 .env.staging 文件
    if [ ! -f ".env.staging" ]; then
        log_error "未找到 .env.staging 文件！"
        echo "请先复制 .env.staging.example 为 .env.staging 并配置环境变量。"
        exit 1
    fi
    
    # 创建数据目录
    mkdir -p data/staging/uploads data/staging/logs
    
    # 确保网络存在 (由 prod 创建)
    if ! docker network inspect multimo-prod-network &> /dev/null; then
        log_warning "网络 multimo-prod-network 不存在，请先部署 Production 环境"
        log_info "创建网络..."
        docker network create multimo-prod-network
    fi
    
    # 构建并启动容器
    log_info "构建并启动 Staging 容器..."
    docker compose -f docker-compose.staging.yml up -d --build
    
    if [ $? -eq 0 ]; then
        log_success "Staging 环境部署成功！"
        echo "访问地址: https://test.sea-ming.com"
    else
        log_error "Staging 部署失败，请检查 Docker 日志"
        exit 1
    fi
}

# 主逻辑
case $ENV in
    prod|production)
        check_certificates
        deploy_prod
        ;;
    staging|test)
        check_certificates
        deploy_staging
        ;;
    all)
        check_certificates
        deploy_prod
        echo ""
        deploy_staging
        ;;
    stop)
        log_info "停止所有服务..."
        docker compose -f docker-compose.prod.yml down
        docker compose -f docker-compose.staging.yml down
        log_success "所有服务已停止"
        ;;
    restart)
        log_info "重启所有服务..."
        docker compose -f docker-compose.prod.yml restart
        docker compose -f docker-compose.staging.yml restart
        log_success "所有服务已重启"
        ;;
    status)
        log_info "服务状态:"
        echo ""
        echo "=== Production ===" 
        docker compose -f docker-compose.prod.yml ps
        echo ""
        echo "=== Staging ==="
        docker compose -f docker-compose.staging.yml ps
        ;;
    logs)
        log_info "显示日志 (Ctrl+C 退出)..."
        docker compose -f docker-compose.prod.yml logs -f --tail=100
        ;;
    *)
        echo "用法: ./deploy.sh [命令]"
        echo ""
        echo "可用命令:"
        echo "  prod, production  - 部署 Production 环境"
        echo "  staging, test     - 部署 Staging 环境"
        echo "  all               - 部署所有环境 (默认)"
        echo "  stop              - 停止所有服务"
        echo "  restart           - 重启所有服务"
        echo "  status            - 查看服务状态"
        echo "  logs              - 查看日志"
        exit 1
        ;;
esac

# 清理未使用的镜像
if [[ "$ENV" == "prod" || "$ENV" == "staging" || "$ENV" == "all" ]]; then
    echo ""
    log_info "清理旧镜像..."
    docker image prune -f
fi

echo ""
echo "=========================================="
log_success "部署完成！"
echo "=========================================="
