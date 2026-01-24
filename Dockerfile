FROM python:3.12-slim

WORKDIR /app

# 필수 패키지 설치 (ffmpeg, gcc 등)
RUN apt-get update && \
    apt-get install -y ffmpeg gcc g++ curl && \
    rm -rf /var/lib/apt/lists/*

# uv 설치 (가장 빠른 패키지 매니저)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 라이브러리 설치
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
