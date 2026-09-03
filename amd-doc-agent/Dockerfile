# 1. 基础镜像
FROM python:3.12-slim

# 2. 设置工作目录
WORKDIR /app

# 3. 复制并安装依赖（先复制requirements，利用Docker缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制项目文件
COPY . .

# 5. 暴露端口
EXPOSE 8501

# 6. 启动命令
CMD ["sh", "-c", "streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0"]