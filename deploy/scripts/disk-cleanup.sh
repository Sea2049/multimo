#!/bin/bash
# ===========================================
# 磁盘清理脚本
# 定期运行以保持磁盘空间健康
# ===========================================

set -e

echo "=========================================="
echo "磁盘清理脚本"
echo "=========================================="

# 显示当前磁盘使用情况
echo ""
echo ">>> 当前磁盘使用情况:"
df -h /

# Docker 清理
echo ""
echo ">>> Docker 清理..."

# 删除未使用的镜像
echo "  - 删除悬空镜像..."
docker image prune -f

# 删除未使用的容器
echo "  - 删除停止的容器..."
docker container prune -f

# 删除未使用的网络
echo "  - 删除未使用的网络..."
docker network prune -f

# 删除构建缓存
echo "  - 删除构建缓存..."
docker builder prune -f --keep-storage 2GB

# 显示 Docker 磁盘使用
echo ""
echo ">>> Docker 磁盘使用详情:"
docker system df

# 清理旧日志（保留最近 7 天）
echo ""
echo ">>> 清理旧应用日志..."
if [ -d "/opt/multimo/data/prod/logs" ]; then
    find /opt/multimo/data/prod/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "  - Prod 日志已清理"
fi

if [ -d "/opt/multimo/data/staging/logs" ]; then
    find /opt/multimo/data/staging/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "  - Staging 日志已清理"
fi

# 清理旧的模拟数据（可选，需要确认）
echo ""
echo ">>> 模拟数据统计:"
if [ -d "/opt/multimo/data/prod/uploads/simulations" ]; then
    sim_count=$(find /opt/multimo/data/prod/uploads/simulations -maxdepth 1 -type d | wc -l)
    sim_size=$(du -sh /opt/multimo/data/prod/uploads/simulations 2>/dev/null | cut -f1)
    echo "  - Prod 模拟数量: $((sim_count - 1))"
    echo "  - Prod 模拟大小: $sim_size"
fi

# 显示清理后的磁盘使用情况
echo ""
echo ">>> 清理后磁盘使用情况:"
df -h /

echo ""
echo "=========================================="
echo "清理完成!"
echo "=========================================="
