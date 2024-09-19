FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py app.py

CMD ["gunicorn",  "app:server", "--timeout 120", "--bind", "0.0.0.0:8000"]
