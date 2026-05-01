# 1. 基础镜像
FROM python:3.12-slim

# 2. 设置工作目录
WORKDIR /app

# Add this line BEFORE the COPY command for requirements.txt
RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 

# 3. 复制并安装依赖（先复制requirements，利用Docker缓存层）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 复制项目文件
COPY . .

# 5. 暴露端口
EXPOSE 8501

# 6. 启动命令
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]