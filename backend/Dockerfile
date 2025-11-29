FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1 libssl-dev libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install PaddleOCR & PaddlePaddle CPU
RUN pip install paddlepaddle paddleocr pillow pandas openpyxl

WORKDIR /app
COPY . .

CMD ["python", "main.py"]