# cli/Dockerfile
FROM python:3.13.3-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
ENTRYPOINT ["python", "main.py"]
