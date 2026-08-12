# Object Detection Service - Container Handoff
# Uses Python 3.11 slim with CPU-only PyTorch
FROM python:3.11-slim

# Install system dependencies for Pillow and torch
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first for layer caching
COPY requirements.txt .

# Install Python dependencies
# Use --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Create directories for runtime artifacts
RUN mkdir -p monitoring logs sample_outputs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Startup command
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
