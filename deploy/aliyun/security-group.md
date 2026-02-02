# 阿里云安全组配置指南

本文档说明 Multimo 项目在阿里云 ECS 上的安全组配置。

## 推荐配置：仅允许 Cloudflare IP

为了最大化安全性，建议只允许 Cloudflare 的 IP 地址访问 80/443 端口。

### 入方向规则

| 优先级 | 协议 | 端口范围 | 授权对象 | 描述 |
|--------|------|----------|----------|------|
| 1 | TCP | 22 | 你的管理 IP/32 | SSH 访问（仅限管理员 IP） |
| 10 | TCP | 80 | Cloudflare IPv4 | HTTP (CF) |
| 10 | TCP | 443 | Cloudflare IPv4 | HTTPS (CF) |
| 10 | TCP | 80 | Cloudflare IPv6 | HTTP (CF IPv6) |
| 10 | TCP | 443 | Cloudflare IPv6 | HTTPS (CF IPv6) |
| 100 | ALL | ALL | 0.0.0.0/0 | 拒绝所有（默认） |

### 出方向规则

| 优先级 | 协议 | 端口范围 | 授权对象 | 描述 |
|--------|------|----------|----------|------|
| 1 | ALL | ALL | 0.0.0.0/0 | 允许所有出站 |

## Cloudflare IP 地址列表

Cloudflare 会定期更新其 IP 地址列表。请从官方获取最新列表：

- **IPv4**: https://www.cloudflare.com/ips-v4
- **IPv6**: https://www.cloudflare.com/ips-v6

### 当前 IPv4 地址段（截至 2024 年）

```
173.245.48.0/20
103.21.244.0/22
103.22.200.0/22
103.31.4.0/22
141.101.64.0/18
108.162.192.0/18
190.93.240.0/20
188.114.96.0/20
197.234.240.0/22
198.41.128.0/17
162.158.0.0/15
104.16.0.0/13
104.24.0.0/14
172.64.0.0/13
131.0.72.0/22
```

### 当前 IPv6 地址段（截至 2024 年）

```
2400:cb00::/32
2606:4700::/32
2803:f800::/32
2405:b500::/32
2405:8100::/32
2a06:98c0::/29
2c0f:f248::/32
```

## 在阿里云控制台配置

### 方法一：手动添加每个 IP 段

1. 登录阿里云控制台
2. 进入 **云服务器 ECS** -> **网络与安全** -> **安全组**
3. 选择实例绑定的安全组，点击 **配置规则**
4. 点击 **手动添加**，为每个 Cloudflare IP 段添加规则

### 方法二：使用脚本批量添加

```bash
#!/bin/bash
# 使用阿里云 CLI 批量添加 Cloudflare IP
# 需要先配置 aliyun CLI

SECURITY_GROUP_ID="sg-xxxxxxxxxx"  # 替换为你的安全组 ID
REGION="cn-hangzhou"               # 替换为你的地域

# Cloudflare IPv4 列表
CF_IPS=(
    "173.245.48.0/20"
    "103.21.244.0/22"
    "103.22.200.0/22"
    "103.31.4.0/22"
    "141.101.64.0/18"
    "108.162.192.0/18"
    "190.93.240.0/20"
    "188.114.96.0/20"
    "197.234.240.0/22"
    "198.41.128.0/17"
    "162.158.0.0/15"
    "104.16.0.0/13"
    "104.24.0.0/14"
    "172.64.0.0/13"
    "131.0.72.0/22"
)

for ip in "${CF_IPS[@]}"; do
    echo "添加 $ip 到安全组..."
    aliyun ecs AuthorizeSecurityGroup \
        --RegionId $REGION \
        --SecurityGroupId $SECURITY_GROUP_ID \
        --IpProtocol tcp \
        --PortRange 80/80 \
        --SourceCidrIp $ip \
        --Description "Cloudflare HTTP"
    
    aliyun ecs AuthorizeSecurityGroup \
        --RegionId $REGION \
        --SecurityGroupId $SECURITY_GROUP_ID \
        --IpProtocol tcp \
        --PortRange 443/443 \
        --SourceCidrIp $ip \
        --Description "Cloudflare HTTPS"
done
```

## 简化配置（不推荐用于生产）

如果你不需要严格的安全性，可以直接开放 80/443 端口给所有 IP：

| 协议 | 端口范围 | 授权对象 | 描述 |
|------|----------|----------|------|
| TCP | 22 | 你的管理 IP/32 | SSH |
| TCP | 80 | 0.0.0.0/0 | HTTP |
| TCP | 443 | 0.0.0.0/0 | HTTPS |

⚠️ **警告**: 这种配置会使你的服务器直接暴露在互联网上，可能遭受 DDoS 攻击。

## 验证配置

配置完成后，可以使用以下命令验证：

```bash
# 从你的本地机器（应该被拒绝，除非你的 IP 在白名单中）
curl -I http://YOUR_ECS_IP

# 通过 Cloudflare 访问（应该成功）
curl -I https://multimo.sea-ming.com
```

## 定期更新

Cloudflare 的 IP 地址可能会变化。建议：

1. 订阅 Cloudflare 的 IP 变更通知
2. 每季度检查一次 IP 列表
3. 使用自动化脚本同步 IP 列表
