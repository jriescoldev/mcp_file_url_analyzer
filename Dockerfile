# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Optionally copy README and other docs
COPY README.md ./

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command: run the MCP server
CMD ["python", "-m", "src.mcp_file_url_analyzer.server"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost', 8080))" || exit 1
