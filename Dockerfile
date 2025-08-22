FROM python:3.9-slim

# 작업 디렉터리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    tzdata \    
    && rm -rf /var/lib/apt/lists/*


ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


# 요구사항 파일 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 프로젝트 파일 복사
COPY . .

# 디렉터리 생성
RUN mkdir -p /app/data/analysis_results /app/logs

# Python 경로 설정
ENV PYTHONPATH=/app

# 기본 명령어 설정
CMD ["python", "run_analysis.py"]