FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    # Tesseract OCR 引擎（用于扫描版 PDF 识别）
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置 Tesseract 路径（Linux 默认位置）
ENV TESSERACT_CMD=/usr/bin/tesseract

# 先安装 PyTorch CPU 版本（节省 ~2GB 空间）
# 必须在其他依赖之前安装，避免 camel-ai 拉取 CUDA 版本
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码（.dockerignore 排除不需要的文件）
COPY . .

# 创建数据目录
RUN mkdir -p uploads/simulations logs

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

EXPOSE 5001

CMD ["python", "run.py"]
