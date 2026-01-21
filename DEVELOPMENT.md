# Multimo 开发指南

## 1. 开发环境搭建

### 1.1 环境要求

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18+ | 前端运行环境，包含 npm |
| Python | ≥3.11, ≤3.12 | 后端运行环境 |
| uv | 最新版 | Python 包管理器 |
| Git | 最新版 | 版本控制 |

### 1.2 克隆项目

```bash
git clone https://github.com/666ghj/Multimo.git
cd Multimo
```

### 1.3 配置环境变量

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，填入必要的 API 密钥
```

**必需的环境变量：**

```env
# LLM API配置（支持 OpenAI SDK 格式的任意 LLM）
# 推荐使用阿里百炼平台qwen-plus模型：https://bailian.console.aliyun.com/
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# Zep Cloud 配置
# 每月免费额度即可支撑简单使用：https://app.getzep.com/
ZEP_API_KEY=your_zep_api_key
```

### 1.4 安装依赖

```bash
# 一键安装所有依赖（根目录 + 前端 + 后端）
npm run setup:all
```

或者分步安装：

```bash
# 安装 Node 依赖（根目录 + 前端）
npm run setup

# 安装 Python 依赖（自动创建虚拟环境）
npm run setup:backend
```

### 1.5 启动开发服务器

```bash
# 同时启动前后端（在项目根目录执行）
npm run dev
```

**服务地址：**
- 前端：http://localhost:3000
- 后端 API：http://localhost:5001

**单独启动：**

```bash
npm run backend   # 仅启动后端
npm run frontend  # 仅启动前端
```

## 2. 项目结构

```
MiroFish/
├── backend/                 # 后端 Python 应用
│   ├── app/                 # 应用核心代码
│   │   ├── api/            # API 路由层
│   │   ├── models/         # 数据模型层
│   │   ├── modules/        # 功能模块（重构）
│   │   ├── services/       # 业务逻辑层
│   │   └── utils/          # 工具函数层
│   ├── scripts/            # 脚本目录
│   ├── uploads/            # 上传文件目录
│   └── logs/               # 日志目录
├── frontend/                # 前端 Vue.js 应用
│   ├── src/
│   │   ├── api/            # API 客户端
│   │   ├── components/     # Vue 组件
│   │   ├── views/          # 页面视图
│   │   ├── router/         # 路由
│   │   └── store/          # 状态管理
│   └── public/             # 公共静态资源
├── docs/                   # 文档目录
├── ARCHITECTURE.md          # 架构文档
├── API.md                  # API 文档
├── DEVELOPMENT.md          # 开发指南（本文件）
├── CODE_DIRECTORY.md       # 代码目录文档
└── README.md               # 中文说明文档
```

详细的目录结构说明请参考 [CODE_DIRECTORY.md](CODE_DIRECTORY.md)

## 3. 开发规范

### 3.1 代码风格

**Python 代码：**
- 遵循 PEP 8 规范
- 使用 4 个空格缩进
- 每行不超过 100 字符
- 使用类型提示（Type Hints）

**JavaScript/Vue 代码：**
- 使用 ESLint 规范
- 使用 2 个空格缩进
- 使用单引号
- 使用箭头函数

### 3.2 命名规范

**Python 文件和变量：**
- 文件名：小写字母和下划线 `service_name.py`
- 类名：大驼峰命名 `ServiceName`
- 函数名：小写字母和下划线 `function_name`
- 常量：大写字母和下划线 `CONSTANT_NAME`

**Vue 组件：**
- 组件名：大驼峰命名 `ComponentName.vue`
- 步骤组件：`Step1GraphBuild.vue`
- 视图组件：`ViewName.vue`

**API 端点：**
- 使用小写字母和连字符 `/api/v1/graph-upload`
- 使用 RESTful 风格

### 3.3 注释规范

**Python 注释：**

```python
# 单行注释：简要说明代码功能

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    从文本中提取实体
    
    Args:
        text: 要分析的文本
        
    Returns:
        包含实体信息的字典列表
        
    Raises:
        ValueError: 当文本为空时
    """
    pass
```

**Vue 注释：**

```vue
<template>
  <!-- 模板注释：说明 UI 元素的作用 -->
  <div>...</div>
</template>

<script>
export default {
  data() {
    return {
      // 数据属性注释
      count: 0
    }
  }
}
</script>
```

### 3.4 Git 提交规范

**提交信息格式：**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）：**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

**示例：**

```
feat(graph): 添加实体提取功能

- 实现基于 LLM 的实体提取器
- 支持多种实体类型识别
- 添加单元测试

Closes #123
```

## 4. 测试

### 4.1 后端测试

```bash
# 进入后端目录
cd backend

# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_graph.py

# 运行特定测试函数
uv run pytest tests/test_graph.py::test_extract_entities

# 查看测试覆盖率
uv run pytest --cov=app --cov-report=html
```

### 4.2 前端测试

```bash
# 进入前端目录
cd frontend

# 运行所有测试
npm run test

# 运行特定测试文件
npm run test -- components/GraphPanel.spec.js
```

### 4.3 集成测试

```bash
# 运行完整的集成测试
npm run test:integration
```

## 5. 调试

### 5.1 后端调试

```bash
# 使用 VS Code 调试
# 在 launch.json 中配置：
{
  "name": "Python: Flask",
  "type": "python",
  "request": "launch",
  "module": "flask",
  "env": {
    "FLASK_APP": "run.py",
    "FLASK_DEBUG": "1"
  },
  "args": ["run", "--no-debugger"]
}
```

### 5.2 前端调试

```bash
# 前端开发服务器已集成热重载
# 使用浏览器开发者工具（F12）进行调试
# 推荐：安装 Vue.js devtools 扩展
```

### 5.3 日志查看

```bash
# 查看后端日志
tail -f backend/logs/$(date +%Y-%m-%d).log

# 查看模拟日志
tail -f backend/uploads/simulations/sim_*/run_state.json
```

## 6. 常见问题

### 6.1 依赖安装失败

**问题**：`npm install` 或 `uv sync` 失败

**解决方案：**
```bash
# 清除 npm 缓存
npm cache clean --force

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 对于 uv，尝试更新 uv
pip install --upgrade uv
```

### 6.2 端口被占用

**问题**：端口 3000 或 5001 被占用

**解决方案：**
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# 或修改端口配置
# 修改 frontend/vite.config.js 中的 server.port
# 修改 backend/app/config.py 中的 FLASK_PORT
```

### 6.3 LLM API 调用失败

**问题**：LLM API 调用超时或失败

**解决方案：**
1. 检查 API 密钥是否正确
2. 检查网络连接
3. 检查 API 配额是否用完
4. 查看 `backend/logs/` 中的详细错误日志

### 6.4 Zep Cloud 连接失败

**问题**：无法连接到 Zep Cloud

**解决方案：**
1. 检查 ZEP_API_KEY 是否正确
2. 检查网络连接
3. 查看 Zep Cloud 服务状态

## 7. 性能优化

### 7.1 后端优化

- 使用连接池管理数据库连接
- 实现异步任务处理
- 添加 API 响应缓存
- 优化数据库查询

### 7.2 前端优化

- 使用路由懒加载
- 组件按需导入
- 图片懒加载
- 使用虚拟滚动处理大列表

## 8. 部署

### 8.1 开发环境部署

```bash
# 启动开发服务器
npm run dev
```

### 8.2 生产环境部署

**后端部署：**

```bash
cd backend

# 使用 Gunicorn 部署
uv run gunicorn -w 4 -b 0.0.0.0:5001 app:app
```

**前端部署：**

```bash
cd frontend

# 构建生产版本
npm run build

# 将 dist 目录部署到 Web 服务器
# 例如：Nginx、Apache、CDN 等
```

### 8.3 Docker 部署（可选）

```bash
# 构建镜像
docker build -t multimo:latest .

# 运行容器
docker run -d -p 3000:3000 -p 5001:5001 \
  -e LLM_API_KEY=your_key \
  -e ZEP_API_KEY=your_key \
  multimo:latest
```

## 9. 贡献指南

### 9.1 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 9.2 代码审查

- 确保代码通过所有测试
- 确保代码符合项目规范
- 添加必要的文档和注释
- 更新相关的文档

### 9.3 问题报告

在报告问题时，请提供：
- 问题描述
- 复现步骤
- 预期行为
- 实际行为
- 环境信息（操作系统、Python 版本等）
- 错误日志

## 10. 资源链接

### 10.1 官方文档

- [Flask 文档](https://flask.palletsprojects.com/)
- [Vue.js 文档](https://vuejs.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Zep Cloud 文档](https://docs.getzep.com/)
- [OASIS 框架文档](https://github.com/camel-ai/oasis)

### 10.2 项目文档

- [架构文档](ARCHITECTURE.md)
- [API 文档](API.md)
- [代码目录文档](CODE_DIRECTORY.md)
- [README](README.md)

### 10.3 社区资源

- GitHub Issues: https://github.com/666ghj/Multimo/issues
- GitHub Discussions: https://github.com/666ghj/Multimo/discussions

## 11. 更新日志

### v1.2.0 (2026-01-20)
- 🎉 正式发布 v1.2.0 稳定版本
- 🚀 完整实现图谱构建功能
- 📊 完善模拟引擎和报告生成模块
- 🔧 优化代码结构和性能
- 📦 完整的测试覆盖
- 🐳 Docker 容器化部署支持

### v1.0.0 (2026-01-20)
- 正式发布 v1.0 版本
- 完整实现核心功能模块
- 添加完整的开发文档
- 前后端分离架构
- 集成 Zep Cloud 和 OASIS

## 12. 许可证

本项目采用 MIT License，详见 [LICENSE](LICENSE) 文件。

## 13. 联系方式

如有问题或建议，请联系：
- 邮箱：multimo@shanda.com
- GitHub Issues: https://github.com/666ghj/Multimo/issues
