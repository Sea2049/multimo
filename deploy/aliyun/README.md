# Multimo 阿里云部署指南

本指南将帮助您在阿里云 ECS 上部署 Multimo 系统，并配置 Cloudflare 进行加速和防护。

## 架构概览

```
用户 (浏览器) 
  ↓
Cloudflare (CDN, WAF, SSL)
  ↓
阿里云 ECS (Ubuntu/CentOS)
  ↓
Docker Compose
  ├─ Nginx (Frontend Container) :80
  └─ Python Flask (Backend Container) :5001
```

## 1. 阿里云 ECS 准备

### 1.1 购买与配置
- **操作系统**: 推荐 Ubuntu 22.04 LTS 或 CentOS 7+
- **规格**: 建议至少 2vCPU, 4GB RAM (运行 LLM 相关任务需要一定内存)
- **安全组**: 
  - 入方向: 开放 TCP 80, 443 (用于 Web 访问)
  - 入方向: 开放 TCP 22 (用于 SSH)

### 1.2 环境初始化
登录服务器，安装 Docker 和 Docker Compose。

**Ubuntu:**
```bash
# 更新源
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 启动 Docker
sudo systemctl enable docker
sudo systemctl start docker
```

## 2. 代码部署

### 2.1 获取代码
将项目代码上传到服务器（可以使用 Git 或 SCP）。
```bash
git clone <your-repo-url> multimo
cd multimo
```

### 2.2 配置环境变量
复制生产环境配置模板：
```bash
cp .env.production.example .env
```
**重要**: 编辑 `.env` 文件，填入您的真实配置：
- `LLM_API_KEY`: 必填
- `SECRET_KEY`: 修改为随机字符串
- `CORS_ORIGINS`: 修改为您的域名 (如 `["https://multimo.yourdomain.com"]`)

### 2.3 启动服务
使用提供的部署脚本或直接运行 Docker Compose：
```bash
# 赋予脚本执行权限
chmod +x deploy.sh

# 启动
./deploy.sh
```

## 3. Cloudflare 配置

### 3.1 DNS 设置
在 Cloudflare 后台：
- 添加 `A` 记录：`multimo` -> 指向您的阿里云 ECS 公网 IP。
- 确保 "Proxy status" 为 **Proxied** (橙色云朵)，这样流量才会经过 Cloudflare。

### 3.2 SSL/TLS 设置
- 进入 **SSL/TLS** -> **Overview**。
- 将模式设置为 **Full** (如果您的 Nginx 配置了自签名证书) 或 **Flexible** (如果 Nginx 只监听 80 端口)。
  - **推荐方案**: Nginx 监听 80 端口，Cloudflare 设置为 **Flexible**。这样 Cloudflare 到 ECS 走 HTTP，Cloudflare 到用户走 HTTPS。
  - **更安全方案**: Nginx 配置自签名证书监听 443，Cloudflare 设置为 **Full**。

### 3.3 页面规则 (可选)
如果遇到 WebSocket 断连或超时问题，可以在 Cloudflare **Rules** 中设置：
- URL: `multimo.yourdomain.com/api/*`
- Setting: `Cache Level` = `Bypass` (不缓存 API 请求)
- Setting: `Proxy Read Timeout` = `300` (延长超时时间)

## 4. 维护与更新

### 查看日志
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 更新代码
```bash
git pull
./deploy.sh
```

### 数据备份
定期备份以下目录：
- `backend/uploads`
- `backend/tasks.db`
- `backend/storage.db`
