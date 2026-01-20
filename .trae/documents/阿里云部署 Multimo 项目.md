# 阿里云部署方案

## 需要创建的文件

### 1. Docker 配置文件
- `Dockerfile` - 后端 Python 应用的 Docker 镜像
- `frontend/Dockerfile` - 前端 Vue 应用的 Docker 镜像  
- `docker-compose.yml` - 编排前后端容器

### 2. Nginx 配置
- `nginx.conf` - 反向代理配置，统一前端和后端访问

### 3. 部署脚本
- `deploy.sh` - 一键部署脚本（支持阿里云）
- `deploy/aliyun/README.md` - 详细的部署文档

### 4. 生产环境配置
- `.env.production` - 生产环境配置模板

## 部署架构
```
用户浏览器 → Nginx (80/443) → 
    ├→ 前端静态文件
    └→ 后端 API (5001) → LLM API + Zep Cloud
```

## 主要功能
- ✅ 使用 Docker 容器化部署
- ✅ Nginx 反向代理 + HTTPS 支持
- ✅ 环境变量管理
- ✅ 数据持久化（uploads 目录）
- ✅ 自动化部署脚本