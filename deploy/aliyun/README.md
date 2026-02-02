# Multimo 阿里云 + Cloudflare 部署指南

本指南将帮助您在阿里云 ECS 上部署 Multimo 系统，并配置 Cloudflare 进行 CDN 加速和 SSL 防护。

## 架构概览

```
用户浏览器
    ↓ HTTPS
Cloudflare (CDN + WAF + SSL)
    ↓ HTTPS (Origin Certificate)
阿里云 ECS (Ubuntu 22.04)
    ↓
┌─────────────────────────────────────────┐
│  Nginx Container (:80, :443)            │
│    ├─ multimo.sea-ming.com → Production │
│    └─ test.sea-ming.com → Staging       │
└─────────────────────────────────────────┘
    ↓
┌──────────────────┐  ┌──────────────────┐
│  Production      │  │  Staging         │
│  ├─ frontend:80  │  │  ├─ frontend:80  │
│  └─ backend:5001 │  │  └─ backend:5002 │
└──────────────────┘  └──────────────────┘
```

## 快速开始

如果你已经准备好所有前置条件，可以直接执行：

```bash
# 1. SSH 到 ECS 服务器
ssh root@your-ecs-ip

# 2. 运行初始化脚本
curl -fsSL https://raw.githubusercontent.com/your-repo/multimo/main/deploy/aliyun/init-ecs.sh | sudo bash

# 3. 克隆代码
cd /opt/multimo
git clone https://github.com/your-repo/multimo.git .

# 4. 复制证书和配置环境变量 (见下方详细说明)

# 5. 部署
./deploy.sh all
```

---

## 详细步骤

### 第一步：阿里云 ECS 准备

#### 1.1 购买 ECS 实例

| 配置项 | 推荐值 |
|--------|--------|
| 地域 | 根据用户分布选择 |
| 操作系统 | Ubuntu 22.04 LTS |
| 规格 | >= 2 vCPU, 4GB RAM |
| 系统盘 | >= 40GB SSD |
| 带宽 | >= 5Mbps (按量计费) |

#### 1.2 配置安全组

参考 [security-group.md](security-group.md) 配置安全组规则。

推荐配置：
- TCP 22: 仅限管理员 IP
- TCP 80/443: 仅限 Cloudflare IP 段

#### 1.3 初始化服务器

```bash
# SSH 登录服务器
ssh root@<ECS公网IP>

# 上传并运行初始化脚本
scp deploy/aliyun/init-ecs.sh root@<ECS_IP>:/tmp/
ssh root@<ECS_IP> "bash /tmp/init-ecs.sh"
```

或直接在服务器上执行：

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker
apt-get install -y docker-compose-plugin git
mkdir -p /opt/multimo
```

---

### 第二步：Cloudflare 配置

详细步骤请参考 [../cloudflare/README.md](../cloudflare/README.md)

#### 2.1 域名托管

1. 在 Cloudflare 添加站点 `sea-ming.com`
2. 到域名注册商修改 NS 记录指向 Cloudflare

#### 2.2 DNS 记录

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | multimo | `<ECS公网IP>` | Proxied |
| A | test | `<ECS公网IP>` | Proxied |

#### 2.3 SSL/TLS 设置

1. 进入 SSL/TLS -> Overview
2. 选择 **Full (strict)**

#### 2.4 生成 Origin Certificate

1. 进入 SSL/TLS -> Origin Server
2. Create Certificate
3. Hostnames: `*.sea-ming.com`, `sea-ming.com`
4. Validity: 15 years
5. **保存证书和私钥**

---

### 第三步：部署代码

#### 3.1 获取代码

```bash
cd /opt/multimo
git clone https://github.com/your-repo/multimo.git .
```

#### 3.2 配置 SSL 证书

```bash
# 创建证书目录
mkdir -p deploy/cloudflare/certs

# 将 Cloudflare Origin Certificate 保存到文件
vim deploy/cloudflare/certs/origin.pem   # 粘贴证书内容
vim deploy/cloudflare/certs/origin.key   # 粘贴私钥内容

# 设置权限
chmod 600 deploy/cloudflare/certs/*
```

#### 3.3 配置环境变量

```bash
# Production 环境
cp .env.production.example .env.production
vim .env.production
```

必须修改的配置：
```ini
SECRET_KEY=<生成一个随机字符串>
LLM_API_KEY=<你的 OpenAI API Key>
CORS_ORIGINS=["https://multimo.sea-ming.com"]
API_KEYS=[{"id": "admin", "key": "<你的API密钥>", "name": "Admin"}]
```

```bash
# Staging 环境
cp .env.staging.example .env.staging
vim .env.staging
```

#### 3.4 部署服务

```bash
# 部署所有环境
./deploy.sh all

# 或单独部署
./deploy.sh prod      # 仅 Production
./deploy.sh staging   # 仅 Staging
```

---

### 第四步：验证部署

#### 4.1 检查容器状态

```bash
./deploy.sh status
```

应该看到所有容器状态为 `Up`:
```
NAME                     STATUS
multimo-nginx            Up
multimo-backend-prod     Up (healthy)
multimo-frontend-prod    Up
multimo-backend-staging  Up (healthy)
multimo-frontend-staging Up
```

#### 4.2 测试访问

```bash
# 测试 Production
curl -I https://multimo.sea-ming.com
curl https://multimo.sea-ming.com/api/health

# 测试 Staging
curl -I https://test.sea-ming.com
curl https://test.sea-ming.com/api/health
```

#### 4.3 检查 SSL 证书

```bash
curl -vI https://multimo.sea-ming.com 2>&1 | grep -A 5 "Server certificate"
```

---

## 常用运维命令

### 部署管理

```bash
./deploy.sh prod      # 部署 Production
./deploy.sh staging   # 部署 Staging
./deploy.sh all       # 部署所有
./deploy.sh stop      # 停止所有
./deploy.sh restart   # 重启所有
./deploy.sh status    # 查看状态
./deploy.sh logs      # 查看日志
```

### 日志查看

```bash
# 实时日志
docker logs -f multimo-backend-prod
docker logs -f multimo-nginx

# 最近 100 行
docker logs --tail 100 multimo-backend-prod

# 指定时间后的日志
docker logs --since 1h multimo-backend-prod
```

### 健康检查

```bash
bash deploy/aliyun/healthcheck.sh
```

### 更新部署

```bash
cd /opt/multimo
git pull
./deploy.sh all
```

### 数据备份

```bash
# 备份 Production 数据
tar -czf backup-prod-$(date +%Y%m%d).tar.gz data/prod/

# 备份 Staging 数据
tar -czf backup-staging-$(date +%Y%m%d).tar.gz data/staging/
```

---

## 故障排查

### 问题：Error 525 - SSL handshake failed

**原因**: Nginx 没有正确配置 Origin Certificate

**解决**:
1. 检查证书文件是否存在：
   ```bash
   ls -la deploy/cloudflare/certs/
   ```
2. 检查 Nginx 配置：
   ```bash
   docker exec multimo-nginx nginx -t
   ```
3. 重启 Nginx：
   ```bash
   docker restart multimo-nginx
   ```

### 问题：Error 521 - Web server is down

**原因**: Cloudflare 无法连接到 ECS

**解决**:
1. 检查安全组是否允许 Cloudflare IP
2. 检查容器是否运行：`docker ps`
3. 检查 Nginx 是否监听 443 端口

### 问题：Error 522 - Connection timed out

**原因**: 服务响应超时

**解决**:
1. 检查后端服务是否正常
2. 检查服务器负载：`htop`
3. 查看后端日志找错误原因

### 问题：API 返回 CORS 错误

**原因**: CORS_ORIGINS 配置不正确

**解决**:
编辑 `.env.production`:
```ini
CORS_ORIGINS=["https://multimo.sea-ming.com"]
```
然后重启后端：
```bash
docker restart multimo-backend-prod
```

### 问题：容器启动后立即退出

**原因**: 配置错误或依赖问题

**解决**:
```bash
# 查看退出原因
docker logs multimo-backend-prod

# 常见原因：
# - .env 文件不存在
# - LLM_API_KEY 未配置
# - 端口冲突
```

---

## 目录结构

```
/opt/multimo/
├── deploy/
│   ├── aliyun/
│   │   ├── README.md          # 本文档
│   │   ├── init-ecs.sh        # ECS 初始化脚本
│   │   ├── security-group.md  # 安全组配置
│   │   ├── server-deploy.sh   # 服务器部署脚本
│   │   └── healthcheck.sh     # 健康检查脚本
│   ├── cloudflare/
│   │   ├── README.md          # Cloudflare 配置指南
│   │   └── certs/             # SSL 证书目录 (不提交到 Git)
│   │       ├── origin.pem
│   │       └── origin.key
│   ├── nginx/
│   │   ├── Dockerfile
│   │   └── nginx.conf         # Nginx 配置
│   ├── logging/
│   │   └── docker-compose.logging.yml
│   └── monitoring/
│       └── README.md          # 监控配置指南
├── data/
│   ├── prod/                  # Production 数据 (不提交到 Git)
│   │   ├── uploads/
│   │   ├── logs/
│   │   ├── tasks.db
│   │   └── storage.db
│   └── staging/               # Staging 数据 (不提交到 Git)
│       ├── uploads/
│       ├── logs/
│       ├── tasks.db
│       └── storage.db
├── docker-compose.prod.yml    # Production 编排
├── docker-compose.staging.yml # Staging 编排
├── .env.production            # Production 环境变量 (不提交到 Git)
├── .env.staging               # Staging 环境变量 (不提交到 Git)
└── deploy.sh                  # 部署脚本
```

---

## 联系与支持

如有问题，请提交 GitHub Issue 或联系管理员。
