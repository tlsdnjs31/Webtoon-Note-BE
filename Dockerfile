FROM python:3.11-slim

# 작업 디렉토리
WORKDIR /app

# requirements 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 전체 복사
COPY . .

# Cloud Run 필수: uvicorn 포트는 무조건 8080
CMD ["uvicorn", "webtoon.main:app", "--host", "0.0.0.0", "--port", "8080"]
