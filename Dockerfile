# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files & enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (including PostgreSQL client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code & ML pipeline
COPY . .

# Set working directory to backend for Django management
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Entrypoint command running Gunicorn web server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
