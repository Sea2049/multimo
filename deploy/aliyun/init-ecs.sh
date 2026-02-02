#!/bin/bash
# ===========================================
# Multimo ECS 环境初始化脚本
# 适用于 Ubuntu 22.04 LTS
# 用法: sudo bash init-ecs.sh
# ===========================================

set -e

echo "=== Multimo ECS 环境初始化 ==="
echo "操作系统: Ubuntu 22.04 LTS"
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 1. 系统更新
echo "📦 [1/6] 更新系统包..."
apt-get update
apt-get upgrade -y

# 2. 安装基础依赖
echo "📦 [2/6] 安装基础依赖..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    vim \
    htop \
    net-tools

# 3. 安装 Docker Engine
echo "🐳 [3/6] 安装 Docker Engine..."
if command -v docker &> /dev/null; then
    echo "Docker 已安装，跳过..."
    docker --version
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# 4. 配置 Docker
echo "⚙️  [4/6] 配置 Docker 服务..."
systemctl enable docker
systemctl start docker

# 添加当前用户到 docker 组（如果不是 root）
if [ -n "$SUDO_USER" ]; then
    usermod -aG docker $SUDO_USER
    echo "已将用户 $SUDO_USER 添加到 docker 组"
fi

# 5. 安装 Docker Compose v2
echo "🐳 [5/6] 安装 Docker Compose..."
if docker compose version &> /dev/null; then
    echo "Docker Compose 已安装，跳过..."
    docker compose version
else
    apt-get install -y docker-compose-plugin
fi

# 6. 创建项目目录
echo "📁 [6/6] 创建项目目录..."
mkdir -p /opt/multimo
mkdir -p /opt/multimo/certs
chmod 755 /opt/multimo

# 验证安装
echo ""
echo "=== 安装验证 ==="
echo "Docker 版本:"
docker --version
echo ""
echo "Docker Compose 版本:"
docker compose version
echo ""

# 输出下一步指引
echo "=== 初始化完成 ==="
echo ""
echo "下一步操作:"
echo "1. 将项目代码克隆到 /opt/multimo:"
echo "   cd /opt/multimo && git clone <your-repo-url> ."
echo ""
echo "2. 将 Cloudflare Origin Certificate 复制到 /opt/multimo/certs/:"
echo "   - origin.pem (证书)"
echo "   - origin.key (私钥)"
echo ""
echo "3. 配置环境变量:"
echo "   cp .env.production.example .env.production"
echo "   vim .env.production"
echo ""
echo "4. 部署服务:"
echo "   ./deploy.sh prod"
echo ""
