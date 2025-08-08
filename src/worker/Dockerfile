FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y nano && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
WORKDIR /app/worker
CMD ["python", "worker.py"]
