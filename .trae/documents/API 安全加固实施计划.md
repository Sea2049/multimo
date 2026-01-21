# API 安全加固实施计划

## 📋 任务概述
为 Multimo 后端 API 添加全面的安全防护措施，包括认证系统、请求限流、输入验证增强和 CORS 安全配置。

## 🔍 当前状态分析

### 已有的安全措施 ✅
1. **输入验证框架**：已有完善的 `validators.py` 模块，包含多种验证器
2. **XSS 防护**：已实现 `sanitize_string()` 和 `sanitize_dict()` 函数
3. **文件上传限制**：已配置 `ALLOWED_EXTENSIONS` 和 `MAX_CONTENT_LENGTH`
4. **CORS 配置**：已在 `config_new.py` 中配置基础 CORS 策略
5. **错误处理**：已有统一的错误处理器

### 需要加强的部分 ⚠️
1. **缺少认证系统**：所有 API 端点目前无需认证即可访问
2. **无请求限流**：容易受到 DDoS 和暴力攻击
3. **输入验证不完整**：部分端点未使用验证器
4. **文件上传安全检查不足**：仅检查扩展名，未检查文件内容
5. **CORS 配置过于宽松**：允许所有来源访问

## 🎯 实施步骤

### 第 1 步：添加认证系统（1.5 小时）

#### 1.1 创建认证模块 `backend/app/api/auth.py`
- 实现 API Key 认证机制
- 实现请求签名验证（可选，用于高安全场景）
- 创建认证装饰器 `@require_api_key`
- 支持多个 API Key（用户级别）

#### 1.2 更新配置文件
- 在 `config_new.py` 中添加认证相关配置：
  - `API_KEY_ENABLED`: 是否启用 API Key 认证
  - `API_KEYS`: 允许的 API Key 列表
  - `API_KEY_HEADER`: API Key 请求头名称（默认 `X-API-Key`）
  - `SIGNATURE_ENABLED`: 是否启用请求签名
  - `SIGNATURE_SECRET`: 签名密钥

#### 1.3 更新 `.env.example`
- 添加示例配置项

### 第 2 步：实现请求限流（1.5 小时）

#### 2.1 安装依赖
- 添加 `Flask-Limiter>=3.5.0` 到 `requirements.txt`

#### 2.2 配置限流中间件
- 在 `backend/app/__init__.py` 中初始化 Flask-Limiter
- 配置存储后端（内存或 Redis）
- 设置全局默认限流策略

#### 2.3 为不同端点配置限流策略
- **文件上传端点**：5 次/分钟
- **LLM 调用端点**（本体生成、报告生成）：10 次/小时
- **查询端点**：100 次/分钟
- **模拟运行端点**：3 次/小时

#### 2.4 更新配置
- 在 `config_new.py` 中添加限流配置：
  - `RATE_LIMIT_ENABLED`: 是否启用限流
  - `RATE_LIMIT_STORAGE`: 存储类型（memory/redis）
  - `RATE_LIMIT_REDIS_URL`: Redis 连接 URL（可选）
  - 各端点的限流策略配置

### 第 3 步：增强输入验证（1 小时）

#### 3.1 扩展验证器功能
- 在 `validators.py` 中添加：
  - `validate_file_upload()`: 文件上传验证（检查 MIME 类型、文件头）
  - `validate_simulation_config()`: 模拟配置验证
  - `validate_graph_id()`: 图谱 ID 格式验证
  - `validate_sql_injection()`: SQL 注入检测

#### 3.2 为所有 API 端点添加验证
- 审查所有使用 `request.get_json()` 的端点
- 使用 `SchemaValidator` 验证请求数据
- 对所有字符串输入使用 `sanitize_string()`

#### 3.3 文件上传安全增强
- 使用 `python-magic` 检查真实文件类型
- 限制文件大小（已有，但需确保所有端点都遵守）
- 生成随机文件名，避免路径遍历攻击
- 扫描上传文件中的恶意内容（基础检查）

### 第 4 步：加固 CORS 配置（0.5 小时）

#### 4.1 更新 CORS 配置
- 在 `config_new.py` 中：
  - 限制 `CORS_ORIGINS` 为具体的前端域名
  - 生产环境禁止 `*` 通配符
  - 配置 `CORS_MAX_AGE` 缓存预检请求
  - 限制允许的 HTTP 方法和请求头

#### 4.2 环境区分
- 开发环境：允许 localhost
- 生产环境：仅允许配置的域名

### 第 5 步：添加安全响应头（0.5 小时）

#### 5.1 在 `__init__.py` 中添加安全响应头中间件
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security`（生产环境）
- `Content-Security-Policy`

## 📁 涉及的文件

### 新建文件
1. `backend/app/api/auth.py` - 认证模块
2. `backend/app/middleware/security.py` - 安全中间件（可选）

### 修改文件
1. `backend/app/__init__.py` - 添加限流和安全中间件
2. `backend/app/config_new.py` - 添加安全配置
3. `backend/app/utils/validators.py` - 增强验证功能
4. `backend/requirements.txt` - 添加依赖
5. `.env.example` - 添加配置示例
6. `backend/app/api/graph.py` - 添加认证和验证
7. `backend/app/api/simulation.py` - 添加认证和验证
8. `backend/app/api/report.py` - 添加认证和验证

## 🔒 安全检查清单

### SQL 注入防护 ✅
- 项目使用 Zep Cloud 和内存存储，无直接 SQL 查询
- 如有数据库查询，使用参数化查询

### XSS 防护 ✅
- 所有用户输入使用 `sanitize_string()` 清理
- API 响应已设置正确的 Content-Type

### CSRF 防护 ⚠️
- API 使用 Token 认证，不依赖 Cookie
- 如使用 Session，需添加 CSRF Token

### 文件上传安全 ✅
- 检查文件类型（扩展名 + MIME）
- 限制文件大小
- 随机文件名
- 隔离存储目录

### 敏感信息保护 ✅
- API Key 和密钥存储在环境变量
- 错误响应不暴露内部信息
- 日志中不记录敏感数据

## ⏱️ 时间估算
- **第 1 步**：1.5 小时
- **第 2 步**：1.5 小时
- **第 3 步**：1 小时
- **第 4 步**：0.5 小时
- **第 5 步**：0.5 小时
- **测试与调试**：1 小时
- **总计**：约 6 小时

## 📝 注意事项

1. **向后兼容**：认证系统默认关闭，通过配置启用
2. **性能影响**：限流使用内存存储，生产环境建议使用 Redis
3. **文档更新**：需要更新 API 文档说明认证方式
4. **测试覆盖**：为所有安全功能编写单元测试
5. **渐进式部署**：先在开发环境测试，再部署到生产环境

## 🚀 后续优化建议

1. **OAuth2 支持**：如需多用户系统，可升级为 OAuth2
2. **JWT Token**：替代简单的 API Key
3. **审计日志**：记录所有 API 访问和敏感操作
4. **IP 白名单**：限制特定 IP 访问
5. **WAF 集成**：使用 Web 应用防火墙