# 阿里云部署实施计划

## 一、准备工作

### 1. 阿里云资源准备
- 购买 ECS 实例（建议配置：4核8G，带宽5Mbps，Ubuntu 22.04）
- 购买域名（可选，用于 Cloudflare 配置）
- 准备 Cloudflare 账号

### 2. 本地文件准备
创建以下配置文件：

#### a) 前端 Nginx 配置 (`frontend/nginx.conf`)
- 配置静态文件服务
- 配置 API 反向代理到后端
- 配置 SPA 路由支持

#### b) Docker Compose 配置 (`docker-compose.yml`)
- 编排前后端容器
- 配置网络和卷挂载
- 配置环境变量

#### c) 生产环境配置 (`.env.production`)
- 配置生产环境变量
- 配置 CORS 域名
- 配置 API 密钥

#### d) 部署脚本 (`deploy/aliyun/deploy.sh`)
- 一键部署脚本
- 自动拉取代码、构建镜像、启动服务

#### e) Nginx 反向代理配置 (`deploy/aliyun/nginx.conf`)
- 宿主机 Nginx 配置
- SSL 证书支持（Cloudflare Origin Certificate）
- 反向代理到容器

## 二、ECS 服务器配置

### 1. 基础环境安装
- 更新系统：`apt update && apt upgrade -y`
- 安装 Docker 和 Docker Compose
- 安装 Nginx
- 配置防火墙（开放 80, 443 端口）

### 2. 目录结构创建
```
/opt/multimo/
├── app/              # 应用代码
├── nginx/            # Nginx 配置
├── data/             # 持久化数据
│   ├── uploads/      # 上传文件
│   └── logs/         # 日志文件
└── docker-compose.yml
```

## 三、应用部署

### 1. 上传代码到 ECS
- 使用 git clone 或 scp 上传代码
- 复制 `.env.production` 到服务器

### 2. 构建和启动容器
- 执行 `docker-compose up -d`
- 检查容器状态：`docker-compose ps`
- 查看日志：`docker-compose logs -f`

### 3. 配置宿主机 Nginx
- 复制 nginx.conf 到 `/etc/nginx/sites-available/multimo`
- 启用配置：`ln -s ... /etc/nginx/sites-enabled/`
- 测试配置：`nginx -t`
- 重启 Nginx：`systemctl restart nginx`

## 四、Cloudflare 配置

### 1. 添加站点到 Cloudflare
- 输入域名并选择套餐（免费版即可）

### 2. DNS 配置
- 添加 A 记录：`@` → ECS 公网 IP
- 代理状态：开启（橙色云朵）

### 3. SSL/TLS 配置
- 模式选择：Full (strict)
- 下载 Origin Certificate 并上传到 ECS

### 4. 安全规则（可选）
- 配置 WAF 规则
- 配置防火墙规则
- 启用 Bot 保护

## 五、监控和维护

### 1. 日志管理
- 配置 Docker 日志轮转
- 定期清理旧日志

### 2. 备份策略
- 定期备份数据库
- 备份上传文件

### 3. 监控告警
- 配置阿里云云监控
- 设置磁盘、CPU、内存告警

---

## 预期成果

完成以上步骤后，你将获得：
- ✅ 在阿里云 ECS 上运行的 Multimo 应用
- ✅ 通过 Cloudflare CDN 加速的访问体验
- ✅ HTTPS 安全加密
- ✅ 基本的 DDoS 和攻击防护
- ✅ 容器化部署，易于维护和扩展

---

## 下一步

确认此计划后，我将：
1. 创建所有缺失的配置文件
2. 编写详细的部署脚本
3. 更新框架文档和代码目录