#!/bin/bash
# ===========================================
# Multimo 健康检查脚本
# 用法: bash healthcheck.sh
# ===========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PROD_BACKEND_URL="http://localhost:5001/api/health"
STAGING_BACKEND_URL="http://localhost:5002/api/health"
DISK_THRESHOLD=80  # 磁盘使用率告警阈值 (%)
MEM_THRESHOLD=80   # 内存使用率告警阈值 (%)

echo ""
echo "=========================================="
echo "    Multimo 健康检查"
echo "    $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 检查结果
ALL_OK=true

# 1. 检查 Docker 服务
echo -e "${BLUE}[1/5] Docker 服务状态${NC}"
if systemctl is-active --quiet docker; then
    echo -e "  ${GREEN}✓${NC} Docker 服务运行中"
else
    echo -e "  ${RED}✗${NC} Docker 服务未运行"
    ALL_OK=false
fi
echo ""

# 2. 检查容器状态
echo -e "${BLUE}[2/5] 容器运行状态${NC}"

check_container() {
    local name=$1
    local status=$(docker inspect -f '{{.State.Status}}' $name 2>/dev/null)
    
    if [ "$status" == "running" ]; then
        local health=$(docker inspect -f '{{.State.Health.Status}}' $name 2>/dev/null)
        if [ "$health" == "healthy" ] || [ "$health" == "" ]; then
            echo -e "  ${GREEN}✓${NC} $name: running"
        else
            echo -e "  ${YELLOW}!${NC} $name: running (health: $health)"
        fi
    elif [ -z "$status" ]; then
        echo -e "  ${YELLOW}-${NC} $name: 不存在"
    else
        echo -e "  ${RED}✗${NC} $name: $status"
        ALL_OK=false
    fi
}

# Production 容器
check_container "multimo-nginx"
check_container "multimo-backend-prod"
check_container "multimo-frontend-prod"

# Staging 容器
check_container "multimo-backend-staging"
check_container "multimo-frontend-staging"
echo ""

# 3. 检查 API 健康端点
echo -e "${BLUE}[3/5] API 健康检查${NC}"

check_api() {
    local name=$1
    local url=$2
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 $url 2>/dev/null)
    
    if [ "$response" == "200" ]; then
        echo -e "  ${GREEN}✓${NC} $name: 200 OK"
    elif [ "$response" == "000" ]; then
        echo -e "  ${YELLOW}-${NC} $name: 无法连接"
    else
        echo -e "  ${RED}✗${NC} $name: HTTP $response"
        ALL_OK=false
    fi
}

check_api "Production API" $PROD_BACKEND_URL
check_api "Staging API" $STAGING_BACKEND_URL
echo ""

# 4. 检查磁盘空间
echo -e "${BLUE}[4/5] 磁盘空间${NC}"

disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$disk_usage" -lt "$DISK_THRESHOLD" ]; then
    echo -e "  ${GREEN}✓${NC} 磁盘使用率: ${disk_usage}%"
else
    echo -e "  ${RED}✗${NC} 磁盘使用率: ${disk_usage}% (超过阈值 ${DISK_THRESHOLD}%)"
    ALL_OK=false
fi

# Docker 数据目录
docker_disk=$(du -sh /var/lib/docker 2>/dev/null | cut -f1)
echo -e "  ${BLUE}ℹ${NC} Docker 数据占用: $docker_disk"
echo ""

# 5. 检查内存使用
echo -e "${BLUE}[5/5] 内存使用${NC}"

mem_info=$(free | grep Mem)
mem_total=$(echo $mem_info | awk '{print $2}')
mem_used=$(echo $mem_info | awk '{print $3}')
mem_percent=$((mem_used * 100 / mem_total))

if [ "$mem_percent" -lt "$MEM_THRESHOLD" ]; then
    echo -e "  ${GREEN}✓${NC} 内存使用率: ${mem_percent}%"
else
    echo -e "  ${YELLOW}!${NC} 内存使用率: ${mem_percent}% (接近阈值 ${MEM_THRESHOLD}%)"
fi

# 显示各容器内存使用
echo -e "  ${BLUE}ℹ${NC} 容器内存使用:"
docker stats --no-stream --format "    {{.Name}}: {{.MemUsage}}" 2>/dev/null | head -10
echo ""

# 总结
echo "=========================================="
if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}✓ 所有检查通过${NC}"
else
    echo -e "${RED}✗ 部分检查失败，请查看上方详情${NC}"
fi
echo "=========================================="

# 返回状态码
if [ "$ALL_OK" = true ]; then
    exit 0
else
    exit 1
fi
