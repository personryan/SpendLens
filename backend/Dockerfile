# Use Python slim image instead of PyTorch (to avoid version conflicts)
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1 libssl-dev libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install numpy for transformes and ML 
RUN pip install numpy

# Install PaddleOCR & dependencies
RUN pip install paddlepaddle paddleocr pillow pandas openpyxl

WORKDIR /app
COPY . .

CMD ["python", "main.py"]