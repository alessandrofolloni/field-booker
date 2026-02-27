FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/submissions/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY services/shared /app/shared

COPY services/submissions/app /app/app

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--reload"]
