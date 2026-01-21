# Zep API Key 更新说明

## 问题描述

当前系统中的 Zep API Key 已过期或无效,导致图谱数据无法加载。错误信息:
```
ApiError: status_code: 401, body: unauthorized
```

## 解决方案

### 1. 获取新的 Zep API Key

访问 [Zep Cloud](https://www.getzep.com/) 并:
1. 登录你的账户
2. 进入 API Keys 管理页面
3. 创建新的 API Key 或复制现有的有效 Key

### 2. 更新配置

有两种方式更新 API Key:

#### 方式 1: 环境变量(推荐)

在系统环境变量或 `.env` 文件中设置:
```bash
LLM_API_KEY=your_new_zep_api_key_here
```

#### 方式 2: 配置文件

编辑 `backend/app/config_new.py`,找到 `LLM_API_KEY` 配置项并更新。

### 3. 重启后端服务

更新配置后,重启 Flask 后端服务:
```bash
cd backend
python run.py
```

## 临时解决方案

如果暂时无法获取新的 API Key,系统已经做了优雅降级处理:
- 图谱数据加载失败不会阻塞报告查看
- 用户会看到友好的错误提示
- 报告的其他功能(如对话、日志查看等)仍然可用

## 验证

更新 API Key 后,可以运行测试脚本验证:
```bash
cd backend
python test_graph_api.py
```

如果配置正确,应该看到:
```
Success!
Node count: XX
Edge count: XX
```

## 相关文件

- 配置文件: `backend/app/config_new.py`
- 图谱服务: `backend/app/services/graph_builder.py`
- API 路由: `backend/app/api/graph.py`
- 测试脚本: `backend/test_graph_api.py`
