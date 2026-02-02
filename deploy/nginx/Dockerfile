# ===========================================
# Multimo Nginx Gateway
# 反向代理 + SSL 终端
# ===========================================

FROM nginx:stable-alpine

# 删除默认配置
RUN rm /etc/nginx/conf.d/default.conf

# 复制自定义配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 创建证书目录
RUN mkdir -p /etc/nginx/certs

# 创建错误页面目录
RUN mkdir -p /usr/share/nginx/html

# 创建简单的错误页面
RUN echo '<!DOCTYPE html><html><head><title>Error</title></head><body><h1>Service Unavailable</h1><p>Please try again later.</p></body></html>' > /usr/share/nginx/html/50x.html

# 暴露端口
EXPOSE 80 443

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
