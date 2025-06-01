FROM python:3.11-slim

WORKDIR /app

COPY worker/requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/worker
CMD ["python", "main.py"]
