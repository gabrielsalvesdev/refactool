# microservices/ai-module/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
CMD ["uvicorn", "ai_model:app", "--host", "0.0.0.0", "--port", "6000"] 
