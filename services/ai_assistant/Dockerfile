FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY services/ai_assistant/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/shared /app/shared
COPY services/ai_assistant/app /app/app

EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]
