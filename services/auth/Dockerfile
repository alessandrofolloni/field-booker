FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared library
COPY services/shared /app/shared

# Copy application
COPY services/auth/app /app/app

# Expose port
EXPOSE 8001

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
