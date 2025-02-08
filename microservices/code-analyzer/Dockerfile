# microservices/code-analyzer/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY microservices/code-analyzer/src/requirements.txt .
RUN pip install -r requirements.txt
COPY microservices/code-analyzer/src/ .
CMD ["uvicorn", "analyzer:app", "--host", "0.0.0.0", "--port", "5000"]
