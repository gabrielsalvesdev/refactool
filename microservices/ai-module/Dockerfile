# microservices/ai-module/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY microservices/ai-module/src/requirements.txt .
RUN pip install -r requirements.txt
COPY microservices/ai-module/src/ .
CMD ["uvicorn", "ai_model:app", "--host", "0. 
