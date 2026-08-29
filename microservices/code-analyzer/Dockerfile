# microservices/code-analyzer/Dockerfile
FROM python:3.14.0rc1-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
CMD ["uvicorn", "analyzer:app", "--host", "0.0.0.0", "--port", "5000"]
