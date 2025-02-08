# cli/Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY cli/src/requirements.txt .
RUN pip install -r requirements.txt
COPY cli/src/ .
ENTRYPOINT ["python", "main.py"]
