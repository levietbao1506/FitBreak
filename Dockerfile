# Sử dụng Python 3.11 slim nhẹ và tối ưu
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Ngăn Python ghi file .pyc và bật log trực tiếp ra console
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/api"

# Cài đặt curl để phục vụ kiểm tra healthcheck nếu cần
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Tận dụng cache của Docker: copy requirements và cài đặt thư viện trước
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng API
EXPOSE 8000

# Khởi chạy server FastAPI
CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

