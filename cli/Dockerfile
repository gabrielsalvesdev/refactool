# cli/Dockerfile
FROM python:3.14.2-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
ENTRYPOINT ["python", "main.py"]
