# syntax=docker/dockerfile:1
FROM python:3.14.2-alpine3.23

WORKDIR /app

# Install system dependencies for Alpine and Python wheels (uncomment if needed)
# RUN apk add --no-cache build-base gcc musl-dev libffi-dev openssl-dev python3-dev cargo rust

# Copy requirements and install Python dependencies
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Optionally copy README and other docs
COPY README.md ./

# Set environment variables (if needed)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command: run the MCP server
CMD ["python", "-m", "src.mcp_file_url_analyzer.server"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('localhost', 8080))" || exit 1
