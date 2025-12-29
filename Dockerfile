# Dockerfile for Barcode Detection Service
FROM python:3.11-slim

# Install system dependencies for pyzbar and pdf2image
RUN apt-get update && apt-get install -y \
    libzbar0 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

