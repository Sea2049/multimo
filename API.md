# Multimo API 文档

## 1. API 概述

Multimo 提供基于 REST 架构的 Web API，支持图谱构建、模拟控制、报告生成和智能体交互等功能。

### 1.1 基础信息

- **Base URL**: `http://localhost:5001/api/v1`
- **Content-Type**: `application/json`
- **认证方式**: 当前版本无需认证（未来将支持 JWT）

### 1.2 通用响应格式

**成功响应：**
```json
{
  "success": true,
  "data": {},
  "message": "操作成功"
}
```

**错误响应：**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### 1.3 HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 2. 图谱 API

### 2.1 上传种子材料

**端点**: `POST /api/v1/graph/upload`

**描述**: 上传种子材料文件（PDF、TXT、Markdown）并提取文本

**请求参数**:
- Content-Type: `multipart/form-data`

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| file | File | 是 | 上传的文件 |
| project_id | String | 否 | 项目 ID（可选） |

**请求示例**:
```bash
curl -X POST http://localhost:5001/api/v1/graph/upload \
  -F "file=@seed_material.pdf"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "project_id": "proj_123456",
    "file_path": "/uploads/projects/proj_123456/files/seed_material.pdf",
    "text_length": 12345,
    "extracted": true
  },
  "message": "文件上传成功"
}
```

### 2.2 提取实体和关系

**端点**: `POST /api/v1/graph/extract`

**描述**: 从上传的文本中提取实体和关系

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 是 | 项目 ID |
| text | String | 是 | 要分析的文本 |

**请求示例**:
```json
{
  "project_id": "proj_123456",
  "text": "这里是要分析的文本内容..."
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "entities": [
      {
        "name": "张三",
        "type": "人物",
        "description": "某公司CEO"
      }
    ],
    "relations": [
      {
        "source": "张三",
        "target": "某公司",
        "type": "就职",
        "description": "担任CEO职位"
      }
    ],
    "graph_id": "graph_789012"
  },
  "message": "实体和关系提取成功"
}
```

### 2.3 获取实体列表

**端点**: `GET /api/v1/graph/entities`

**描述**: 获取项目中的所有实体

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 是 | 项目 ID |
| type | String | 否 | 筛选实体类型 |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/graph/entities?project_id=proj_123456"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "entities": [
      {
        "name": "张三",
        "type": "人物",
        "description": "某公司CEO"
      },
      {
        "name": "某公司",
        "type": "组织",
        "description": "一家科技公司"
      }
    ],
    "total": 2
  },
  "message": "获取实体列表成功"
}
```

### 2.4 获取关系列表

**端点**: `GET /api/v1/graph/relationships`

**描述**: 获取项目中的所有关系

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 是 | 项目 ID |
| entity | String | 否 | 筛选特定实体的关系 |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/graph/relationships?project_id=proj_123456"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "relationships": [
      {
        "source": "张三",
        "target": "某公司",
        "type": "就职",
        "description": "担任CEO职位"
      }
    ],
    "total": 1
  },
  "message": "获取关系列表成功"
}
```

### 2.5 导出图谱数据

**端点**: `GET /api/v1/graph/export`

**描述**: 导出知识图谱数据

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 是 | 项目 ID |
| format | String | 否 | 导出格式（json/gexf） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/graph/export?project_id=proj_123456&format=json"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "张三",
        "type": "人物",
        "attributes": {}
      }
    ],
    "edges": [
      {
        "source": "张三",
        "target": "某公司",
        "type": "就职"
      }
    ]
  },
  "message": "图谱导出成功"
}
```

## 3. 模拟 API

### 3.1 生成模拟配置

**端点**: `POST /api/v1/simulation/config`

**描述**: 基于图谱生成模拟配置

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 是 | 项目 ID |
| platforms | Array | 是 | 模拟平台列表（twitter/reddit） |
| num_agents | Integer | 否 | 智能体数量（默认：10） |
| max_rounds | Integer | 否 | 最大轮次（默认：10） |

**请求示例**:
```json
{
  "project_id": "proj_123456",
  "platforms": ["twitter", "reddit"],
  "num_agents": 20,
  "max_rounds": 15
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_789012",
    "config": {
      "platforms": ["twitter", "reddit"],
      "num_agents": 20,
      "max_rounds": 15,
      "agents": [
        {
          "name": "Agent_1",
          "platform": "twitter",
          "profile": {}
        }
      ]
    },
    "ready": true
  },
  "message": "模拟配置生成成功"
}
```

### 3.2 启动模拟

**端点**: `POST /api/v1/simulation/start`

**描述**: 启动模拟任务

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |

**请求示例**:
```json
{
  "simulation_id": "sim_789012"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_789012",
    "status": "running",
    "started_at": "2026-01-20T10:00:00Z"
  },
  "message": "模拟启动成功"
}
```

### 3.3 获取模拟状态

**端点**: `GET /api/v1/simulation/status`

**描述**: 获取模拟运行状态

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/simulation/status?simulation_id=sim_789012"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_789012",
    "status": "running",
    "current_round": 5,
    "total_rounds": 15,
    "agents_count": 20,
    "platforms": {
      "twitter": {
        "status": "running",
        "posts": 45
      },
      "reddit": {
        "status": "running",
        "posts": 32
      }
    },
    "started_at": "2026-01-20T10:00:00Z",
    "updated_at": "2026-01-20T10:05:00Z"
  },
  "message": "获取模拟状态成功"
}
```

**状态说明**:
- `idle`: 空闲
- `initializing`: 初始化中
- `running`: 运行中
- `paused`: 暂停
- `completed`: 完成
- `stopped`: 已停止
- `error`: 错误

### 3.4 停止模拟

**端点**: `POST /api/v1/simulation/stop`

**描述**: 停止正在运行的模拟

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |

**请求示例**:
```json
{
  "simulation_id": "sim_789012"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_789012",
    "status": "stopped",
    "stopped_at": "2026-01-20T10:10:00Z"
  },
  "message": "模拟已停止"
}
```

### 3.5 获取模拟日志

**端点**: `GET /api/v1/simulation/logs`

**描述**: 获取模拟运行日志

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |
| limit | Integer | 否 | 返回日志条数（默认：100） |
| offset | Integer | 否 | 偏移量（默认：0） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/simulation/logs?simulation_id=sim_789012&limit=50"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulation_id": "sim_789012",
    "logs": [
      {
        "timestamp": "2026-01-20T10:01:00Z",
        "level": "INFO",
        "message": "模拟开始",
        "round": 1
      },
      {
        "timestamp": "2026-01-20T10:01:30Z",
        "level": "INFO",
        "message": "Agent_1 发布推文",
        "round": 1
      }
    ],
    "total": 150,
    "limit": 50,
    "offset": 0
  },
  "message": "获取模拟日志成功"
}
```

### 3.6 与智能体对话

**端点**: `POST /api/v1/simulation/chat`

**描述**: 与模拟世界中的智能体进行对话

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |
| agent_id | String | 是 | 智能体 ID |
| message | String | 是 | 用户消息 |
| chat_type | String | 否 | 对话类型（agent/system） |

**请求示例**:
```json
{
  "simulation_id": "sim_789012",
  "agent_id": "Agent_1",
  "message": "你好，请问你对这件事有什么看法？",
  "chat_type": "agent"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "agent_id": "Agent_1",
    "response": "我认为这是一个值得关注的事件...",
    "timestamp": "2026-01-20T10:15:00Z"
  },
  "message": "对话成功"
}
```

### 3.7 获取历史模拟

**端点**: `GET /api/v1/simulation/history`

**描述**: 获取历史模拟列表

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| project_id | String | 否 | 项目 ID（筛选） |
| limit | Integer | 否 | 返回数量（默认：20） |
| offset | Integer | 否 | 偏移量（默认：0） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/simulation/history?limit=10"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "simulations": [
      {
        "simulation_id": "sim_789012",
        "project_id": "proj_123456",
        "status": "completed",
        "platforms": ["twitter", "reddit"],
        "num_agents": 20,
        "max_rounds": 15,
        "created_at": "2026-01-20T10:00:00Z",
        "completed_at": "2026-01-20T10:30:00Z"
      }
    ],
    "total": 5,
    "limit": 10,
    "offset": 0
  },
  "message": "获取历史模拟成功"
}
```

## 4. 报告 API

### 4.1 生成报告

**端点**: `POST /api/v1/report/generate`

**描述**: 基于模拟结果生成预测报告

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID |
| query | String | 是 | 预测问题或查询 |
| report_type | String | 否 | 报告类型（full/summary） |

**请求示例**:
```json
{
  "simulation_id": "sim_789012",
  "query": "请分析模拟结果并预测未来的发展趋势",
  "report_type": "full"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_345678",
    "simulation_id": "sim_789012",
    "status": "generating",
    "created_at": "2026-01-20T10:35:00Z"
  },
  "message": "报告生成任务已启动"
}
```

### 4.2 获取报告

**端点**: `GET /api/v1/report/{simulation_id}`

**描述**: 获取模拟的预测报告（JSON 格式）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID（路径参数） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/report/sim_789012"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_345678",
    "simulation_id": "sim_789012",
    "query": "请分析模拟结果并预测未来的发展趋势",
    "content": {
      "title": "预测报告",
      "summary": "报告摘要...",
      "sections": [
        {
          "section_id": 1,
          "title": "模拟过程概述",
          "content": "内容..."
        },
        {
          "section_id": 2,
          "title": "关键发现",
          "content": "内容..."
        }
      ],
      "conclusion": "结论...",
      "recommendations": ["建议1", "建议2"]
    },
    "generated_at": "2026-01-20T10:40:00Z"
  },
  "message": "获取报告成功"
}
```

### 4.3 获取报告（Markdown 格式）

**端点**: `GET /api/v1/report/{simulation_id}/markdown`

**描述**: 获取模拟的预测报告（Markdown 格式）

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 是 | 模拟 ID（路径参数） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/report/sim_789012/markdown"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "report_id": "report_345678",
    "simulation_id": "sim_789012",
    "markdown": "# 预测报告\n\n## 模拟过程概述\n...",
    "generated_at": "2026-01-20T10:40:00Z"
  },
  "message": "获取报告成功"
}
```

### 4.4 列出所有报告

**端点**: `GET /api/v1/report/list`

**描述**: 获取所有报告列表

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| simulation_id | String | 否 | 模拟 ID（筛选） |
| limit | Integer | 否 | 返回数量（默认：20） |
| offset | Integer | 否 | 偏移量（默认：0） |

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/report/list?limit=10"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "reports": [
      {
        "report_id": "report_345678",
        "simulation_id": "sim_789012",
        "query": "请分析模拟结果并预测未来的发展趋势",
        "status": "completed",
        "created_at": "2026-01-20T10:35:00Z",
        "generated_at": "2026-01-20T10:40:00Z"
      }
    ],
    "total": 3,
    "limit": 10,
    "offset": 0
  },
  "message": "获取报告列表成功"
}
```

## 5. 健康检查 API

### 5.1 健康检查

**端点**: `GET /api/v1/health`

**描述**: 检查 API 服务健康状态

**请求示例**:
```bash
curl "http://localhost:5001/api/v1/health"
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "2026-01-20T10:00:00Z",
    "services": {
      "database": "connected",
      "zep_cloud": "connected",
      "llm": "available"
    }
  },
  "message": "服务运行正常"
}
```

## 6. 错误码说明

| 错误码 | 说明 | HTTP 状态码 |
|-------|------|------------|
| INVALID_PARAMS | 请求参数无效 | 400 |
| MISSING_REQUIRED_FIELD | 缺少必填字段 | 400 |
| FILE_NOT_FOUND | 文件不存在 | 404 |
| PROJECT_NOT_FOUND | 项目不存在 | 404 |
| SIMULATION_NOT_FOUND | 模拟不存在 | 404 |
| REPORT_NOT_FOUND | 报告不存在 | 404 |
| SIMULATION_ALREADY_RUNNING | 模拟已在运行中 | 400 |
| SIMULATION_NOT_RUNNING | 模拟未运行 | 400 |
| INTERNAL_ERROR | 内部服务器错误 | 500 |
| LLM_API_ERROR | LLM API 调用失败 | 500 |
| ZEP_API_ERROR | Zep API 调用失败 | 500 |

## 7. 使用示例

### 7.1 完整工作流程

```javascript
// 1. 上传种子材料
const uploadResponse = await fetch('http://localhost:5001/api/v1/graph/upload', {
  method: 'POST',
  body: formData
});
const { data: { project_id } } = await uploadResponse.json();

// 2. 提取实体和关系
const extractResponse = await fetch('http://localhost:5001/api/v1/graph/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_id,
    text: extractedText
  })
});

// 3. 生成模拟配置
const configResponse = await fetch('http://localhost:5001/api/v1/simulation/config', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_id,
    platforms: ['twitter', 'reddit'],
    num_agents: 20,
    max_rounds: 15
  })
});
const { data: { simulation_id } } = await configResponse.json();

// 4. 启动模拟
await fetch('http://localhost:5001/api/v1/simulation/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ simulation_id })
});

// 5. 轮询获取模拟状态
const checkStatus = async () => {
  const statusResponse = await fetch(`http://localhost:5001/api/v1/simulation/status?simulation_id=${simulation_id}`);
  const { data } = await statusResponse.json();
  return data.status;
};

// 6. 模拟完成后生成报告
const reportResponse = await fetch('http://localhost:5001/api/v1/report/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    simulation_id,
    query: '请分析模拟结果并预测未来的发展趋势',
    report_type: 'full'
  })
});

// 7. 获取报告
const reportData = await fetch(`http://localhost:5001/api/v1/report/${simulation_id}`);
const report = await reportData.json();
```

## 8. 版本历史

### v1.0.0 (2026-01-20)
- 正式发布 v1.0 API
- 完整实现图谱构建 API
- 完整实现模拟控制 API
- 完整实现报告生成 API
- 添加健康检查 API
- 支持智能体对话 API

## 9. 后续计划

- [ ] 添加 WebSocket 支持（实时推送模拟状态）
- [ ] 添加 API 认证和授权
- [ ] 添加 API 限流
- [ ] 添加批量操作 API
- [ ] 添加导出更多格式的 API
