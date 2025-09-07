# Main Dockerfile for AI Swarm Intelligence System
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install additional AI/ML dependencies
RUN pip install --no-cache-dir \
    anthropic \
    openai \
    aiohttp \
    python-dotenv \
    prometheus-client \
    psutil \
    redis

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /data /logs /config /backups

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SWARM_HOME=/app
ENV DATABASE_PATH=/data/unified_swarm.db

# Expose ports
EXPOSE 8000 8001 8002

# Health check script
COPY docker_health_check.py /app/

# Entry point script
COPY docker-entrypoint.py /app/
RUN chmod +x /app/docker-entrypoint.py

# Entry point
CMD ["python", "docker-entrypoint.py"]