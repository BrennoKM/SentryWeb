FROM python:3.11-slim

WORKDIR /app

COPY scheduler/requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
WORKDIR /app/scheduler
CMD ["python", "main.py"]
