# Cloudflare 配置指南

本文档说明如何将域名托管到 Cloudflare 并配置 Full (Strict) SSL。

## 1. 域名托管到 Cloudflare

### 1.1 添加站点

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 点击 **Add a Site**
3. 输入域名: `sea-ming.com`
4. 选择计划（Free 即可）
5. Cloudflare 会扫描现有 DNS 记录

### 1.2 修改 NS 记录

Cloudflare 会提供两个 NS 服务器地址，例如：
- `xxx.ns.cloudflare.com`
- `yyy.ns.cloudflare.com`

到域名注册商处修改 NS 记录指向 Cloudflare。

> **注意**: NS 记录生效可能需要 24-48 小时，但通常 1-2 小时内即可生效。

## 2. DNS 记录配置

在 Cloudflare **DNS** -> **Records** 中添加以下记录：

| Type | Name | Content | Proxy | TTL |
|------|------|---------|-------|-----|
| A | multimo | `<ECS公网IP>` | Proxied (橙色云) | Auto |
| A | test | `<ECS公网IP>` | Proxied (橙色云) | Auto |

### 示例

假设 ECS 公网 IP 为 `47.100.xxx.xxx`：

```
multimo.sea-ming.com -> 47.100.xxx.xxx (Proxied)
test.sea-ming.com    -> 47.100.xxx.xxx (Proxied)
```

## 3. SSL/TLS 配置

### 3.1 设置加密模式

1. 进入 **SSL/TLS** -> **Overview**
2. 选择 **Full (strict)**

```
┌─────────────────────────────────────────────────────────────┐
│  SSL/TLS encryption mode                                    │
│                                                             │
│  ○ Off (not secure)                                        │
│  ○ Flexible                                                │
│  ○ Full                                                    │
│  ● Full (strict)  <-- 选择这个                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 生成 Origin Certificate

Origin Certificate 是 Cloudflare 签发的证书，用于 Cloudflare 与你的服务器之间的加密通信。

1. 进入 **SSL/TLS** -> **Origin Server**
2. 点击 **Create Certificate**
3. 配置选项：
   - **Private key type**: RSA (2048)
   - **Hostnames**: 
     - `*.sea-ming.com`
     - `sea-ming.com`
   - **Certificate Validity**: 15 years（推荐最长有效期）

4. 点击 **Create**

5. **重要**: 复制并保存证书和私钥！
   - **Origin Certificate** (PEM 格式) -> 保存为 `origin.pem`
   - **Private Key** (PEM 格式) -> 保存为 `origin.key`

> ⚠️ **警告**: 私钥只显示一次！请务必保存好。如果丢失，需要重新生成证书。

## 4. 页面规则配置（可选但推荐）

### 4.1 API 路径禁用缓存

为了确保 API 请求不被缓存：

1. 进入 **Rules** -> **Page Rules**
2. 点击 **Create Page Rule**
3. 配置：
   - **URL**: `*sea-ming.com/api/*`
   - **Settings**:
     - Cache Level: Bypass
     - Browser Cache TTL: Respect Existing Headers

### 4.2 增加超时时间（针对长时间运行的 API）

如果有长时间运行的 API（如 LLM 生成），可以配置：

1. 进入 **Rules** -> **Page Rules**
2. 添加规则：
   - **URL**: `*sea-ming.com/api/simulation/*`
   - **Settings**:
     - Proxy Read Timeout: 300 seconds

> **注意**: Proxy Read Timeout 需要 Enterprise 计划。Free 计划默认 100 秒超时。

## 5. 安全设置（推荐）

### 5.1 启用 HSTS

1. 进入 **SSL/TLS** -> **Edge Certificates**
2. 启用 **HTTP Strict Transport Security (HSTS)**
3. 配置：
   - Max Age: 6 months
   - Include subdomains: Yes
   - Preload: Yes（可选）

### 5.2 最小 TLS 版本

1. 在 **SSL/TLS** -> **Edge Certificates**
2. 设置 **Minimum TLS Version**: TLS 1.2

### 5.3 启用 Always Use HTTPS

1. 在 **SSL/TLS** -> **Edge Certificates**
2. 启用 **Always Use HTTPS**

## 6. 验证配置

### 6.1 检查 DNS 解析

```bash
# 检查 DNS 是否指向 Cloudflare
dig multimo.sea-ming.com

# 应该返回 Cloudflare 的 IP，而不是你的 ECS IP
```

### 6.2 检查 SSL 证书

```bash
# 检查证书信息
curl -vI https://multimo.sea-ming.com 2>&1 | grep -A 5 "Server certificate"

# 应该显示 Cloudflare 签发的证书
```

### 6.3 检查 Origin 连接

如果配置正确，访问 `https://multimo.sea-ming.com` 应该：
1. 浏览器显示安全锁标志
2. 证书由 Cloudflare 签发
3. 页面正常加载

## 常见问题

### Q: 显示 "Error 525: SSL handshake failed"

**原因**: 服务器没有正确配置 Origin Certificate。

**解决**: 
1. 确认证书文件已正确复制到服务器
2. 确认 Nginx 配置中证书路径正确
3. 重启 Nginx 容器

### Q: 显示 "Error 521: Web server is down"

**原因**: Cloudflare 无法连接到你的服务器。

**解决**:
1. 检查 ECS 安全组是否允许 Cloudflare IP
2. 检查 Docker 容器是否正常运行
3. 检查 Nginx 是否监听正确端口

### Q: 显示 "Error 522: Connection timed out"

**原因**: 服务器响应太慢。

**解决**:
1. 检查服务器负载
2. 检查后端服务是否正常
3. 考虑增加 Cloudflare 超时时间
