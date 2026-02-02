# Multimo 监控方案

本文档介绍 Multimo 项目的监控和告警配置方案。

## 监控架构

```
┌─────────────────────────────────────────────────────────────┐
│                      监控数据来源                            │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  Cloudflare │   阿里云     │   Docker    │   应用日志        │
│  Analytics  │   云监控     │   Stats     │                  │
└─────────────┴─────────────┴─────────────┴──────────────────┘
```

## 1. Cloudflare Analytics（推荐）

Cloudflare 提供免费的流量分析和安全监控。

### 1.1 访问方式

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 选择域名 `sea-ming.com`
3. 进入 **Analytics & Logs**

### 1.2 可监控指标

| 指标 | 说明 |
|------|------|
| Requests | 请求数量和趋势 |
| Bandwidth | 带宽使用情况 |
| Threats | 安全威胁统计 |
| Performance | 性能指标 (TTFB, 加载时间) |
| Cache | 缓存命中率 |

### 1.3 告警配置

1. 进入 **Notifications**
2. 创建告警规则：
   - DDoS 攻击告警
   - 源站不可达告警
   - SSL 证书即将过期告警

## 2. 阿里云云监控

### 2.1 基础监控（免费）

ECS 实例自动开启以下监控：

| 指标 | 建议阈值 |
|------|----------|
| CPU 使用率 | > 80% 告警 |
| 内存使用率 | > 80% 告警 |
| 磁盘使用率 | > 85% 告警 |
| 网络带宽 | 根据实际配置 |

### 2.2 配置告警规则

1. 登录阿里云控制台
2. 进入 **云监控** -> **报警服务** -> **报警规则**
3. 创建规则：

```
规则名称: Multimo-ECS-CPU告警
资源范围: 实例
监控项: CPU使用率
统计周期: 5分钟
连续周期: 3
阈值: > 80%
通知方式: 邮件/短信/钉钉
```

### 2.3 推荐告警规则

| 规则名称 | 监控项 | 条件 | 级别 |
|----------|--------|------|------|
| CPU 高负载 | CPU 使用率 | > 80%, 持续 15 分钟 | 警告 |
| CPU 严重 | CPU 使用率 | > 95%, 持续 5 分钟 | 严重 |
| 内存不足 | 内存使用率 | > 85%, 持续 10 分钟 | 警告 |
| 磁盘空间 | 磁盘使用率 | > 85% | 警告 |
| 磁盘严重 | 磁盘使用率 | > 95% | 严重 |

## 3. Docker 容器监控

### 3.1 使用 healthcheck.sh

```bash
# 运行健康检查
bash /opt/multimo/deploy/aliyun/healthcheck.sh

# 定时检查 (crontab)
*/5 * * * * /opt/multimo/deploy/aliyun/healthcheck.sh >> /var/log/multimo-health.log 2>&1
```

### 3.2 Docker 命令

```bash
# 查看容器状态
docker ps -a

# 查看资源使用
docker stats

# 查看特定容器日志
docker logs -f --tail 100 multimo-backend-prod

# 查看容器健康状态
docker inspect --format='{{.State.Health.Status}}' multimo-backend-prod
```

## 4. 应用层监控

### 4.1 健康检查端点

应用提供以下健康检查端点：

| 端点 | 用途 |
|------|------|
| `/api/health` | 后端健康检查 |
| `/health` | Nginx 健康检查 |

### 4.2 监控脚本

```bash
#!/bin/bash
# 简单的可用性监控

ENDPOINTS=(
    "https://multimo.sea-ming.com/health"
    "https://multimo.sea-ming.com/api/health"
    "https://test.sea-ming.com/health"
    "https://test.sea-ming.com/api/health"
)

for endpoint in "${ENDPOINTS[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint")
    if [ "$status" != "200" ]; then
        echo "ALERT: $endpoint returned $status"
        # 发送告警 (邮件/钉钉/企业微信等)
    fi
done
```

## 5. 日志管理

### 5.1 日志位置

| 日志类型 | 位置 |
|----------|------|
| Docker 容器日志 | `/var/lib/docker/containers/<id>/*-json.log` |
| 应用日志 (prod) | `/opt/multimo/data/prod/logs/` |
| 应用日志 (staging) | `/opt/multimo/data/staging/logs/` |
| Nginx 日志 | Docker 容器内 `/var/log/nginx/` |

### 5.2 日志查看命令

```bash
# 查看后端日志
docker logs -f multimo-backend-prod

# 查看最近 100 行
docker logs --tail 100 multimo-backend-prod

# 查看指定时间后的日志
docker logs --since 2024-01-01T00:00:00 multimo-backend-prod

# 查看 Nginx 日志
docker exec multimo-nginx cat /var/log/nginx/access.log
```

### 5.3 日志清理

```bash
# 清理 Docker 日志 (需要 root)
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# 清理应用日志
find /opt/multimo/data/*/logs -name "*.log" -mtime +30 -delete
```

## 6. 告警通知渠道

### 6.1 钉钉机器人

1. 创建钉钉群
2. 添加自定义机器人，获取 Webhook URL
3. 配置告警脚本：

```bash
#!/bin/bash
WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=xxx"

send_alert() {
    curl -H "Content-Type: application/json" -d "{
        \"msgtype\": \"text\",
        \"text\": {\"content\": \"[Multimo告警] $1\"}
    }" $WEBHOOK
}

send_alert "服务器 CPU 使用率超过 80%"
```

### 6.2 邮件告警

阿里云云监控支持直接配置邮件告警，在创建告警规则时选择通知方式为邮件即可。

## 7. 推荐监控清单

| 类别 | 监控项 | 工具 | 优先级 |
|------|--------|------|--------|
| 可用性 | 网站是否可访问 | Cloudflare / 云监控 | P0 |
| 性能 | API 响应时间 | Cloudflare Analytics | P1 |
| 资源 | CPU/内存/磁盘 | 阿里云云监控 | P1 |
| 容器 | 容器运行状态 | healthcheck.sh | P1 |
| 安全 | 异常请求/攻击 | Cloudflare Security | P2 |
| 日志 | 错误日志 | 应用日志 | P2 |
