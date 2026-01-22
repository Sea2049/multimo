#!/bin/bash

# Multimo 部署脚本
# 用法: ./deploy.sh

echo "=== 开始部署 Multimo ==="

# 1. 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件！"
    echo "请先复制 .env.production.example 为 .env 并配置环境变量。"
    exit 1
fi

# 2. 拉取最新代码 (如果是 git 仓库)
if [ -d .git ]; then
    echo "⬇️  拉取最新代码..."
    git pull
else
    echo "ℹ️  未检测到 git 仓库，跳过代码拉取。"
fi

# 3. 构建并启动容器
echo "🐳 构建并启动 Docker 容器..."
# --build: 强制重新构建镜像
# -d: 后台运行
docker-compose up -d --build

# 4. 检查运行状态
if [ $? -eq 0 ]; then
    echo "✅ 部署成功！"
    echo "后端服务运行在: http://localhost:5001"
    echo "前端服务运行在: http://localhost:80"
    
    echo "正在检查容器状态..."
    docker-compose ps
else
    echo "❌ 部署失败，请检查 Docker 日志。"
    exit 1
fi

# 5. 清理未使用的镜像 (可选)
echo "🧹 清理旧镜像..."
docker image prune -f

echo "=== 部署完成 ==="
