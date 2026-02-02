# Cloudflare Origin Certificate 存放说明

此目录用于存放 Cloudflare Origin Certificate 文件。

## 文件命名

| 文件名 | 描述 | 来源 |
|--------|------|------|
| `origin.pem` | SSL 证书（公钥） | Cloudflare Origin Certificate |
| `origin.key` | SSL 私钥 | Cloudflare Origin Certificate |

## 获取证书

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 选择域名 `sea-ming.com`
3. 进入 **SSL/TLS** -> **Origin Server**
4. 点击 **Create Certificate**
5. 配置：
   - Hostnames: `*.sea-ming.com`, `sea-ming.com`
   - Validity: 15 years
6. 复制 **Origin Certificate** 内容，保存为 `origin.pem`
7. 复制 **Private Key** 内容，保存为 `origin.key`

## 文件格式

### origin.pem 示例

```
-----BEGIN CERTIFICATE-----
MIIEpDCCA4ygAwIBAgIUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
... (证书内容)
-----END CERTIFICATE-----
```

### origin.key 示例

```
-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCxxxxxxxxxxxxxxxx
... (私钥内容)
-----END PRIVATE KEY-----
```

## 安全警告

⚠️ **重要安全提示**:

1. **永远不要将此目录下的文件提交到 Git 仓库**
2. 这些文件已在 `.gitignore` 中被忽略
3. 在服务器上，证书文件应设置为只读权限：
   ```bash
   chmod 600 origin.pem origin.key
   ```

## 部署到服务器

将证书文件复制到服务器：

```bash
# 使用 SCP 复制
scp origin.pem origin.key user@your-ecs-ip:/opt/multimo/certs/

# 或者手动创建
ssh user@your-ecs-ip
cd /opt/multimo/certs/
vim origin.pem  # 粘贴证书内容
vim origin.key  # 粘贴私钥内容
chmod 600 origin.pem origin.key
```

## 证书更新

Origin Certificate 有效期最长 15 年。如需更新：

1. 在 Cloudflare 控制台撤销旧证书
2. 生成新证书
3. 替换服务器上的证书文件
4. 重启 Nginx 容器：
   ```bash
   docker compose restart nginx
   ```
