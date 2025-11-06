FROM vllm/vllm-openai:latest

# 필요한 추가 패키지 설치
RUN pip install --no-cache-dir \
    numpy \
    pillow

# 작업 디렉토리 설정
WORKDIR /app

# 헬스체크를 위한 curl 설치
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 로그 디렉토리 생성
RUN mkdir -p /logs

# 환경변수 설정
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/models

EXPOSE 8000
