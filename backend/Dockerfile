# Multi-stage Dockerfile for Backend Service
# Stage 1: Base Python image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Stage 2: Dependencies installation
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 3: Build stage
FROM base as build

# Set working directory
WORKDIR /app

# Copy dependencies from previous stage
COPY --from=dependencies /root/.local /root/.local

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/chroma_db /app/logs

# Set permissions
RUN chown -R app:app /app

# Stage 4: Production runtime
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    APP_ENV=production

# Install runtime system dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy Python dependencies from build stage
COPY --from=build /root/.local /root/.local

# Copy application code
COPY --from=build /app /app

# Copy necessary directories
COPY --from=build /app/data /app/data
COPY --from=build /app/chroma_db /app/chroma_db
COPY --from=build /app/logs /app/logs

# Set proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
