FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    # Tesseract OCR 引擎（用于扫描版 PDF 识别）
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 设置 Tesseract 路径（Linux 默认位置）
ENV TESSERACT_CMD=/usr/bin/tesseract

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/simulations

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

EXPOSE 5001

CMD ["python", "run.py"]
