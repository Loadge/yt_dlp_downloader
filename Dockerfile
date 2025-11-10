# Multi-stage build for smaller image size
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

# Install FFmpeg and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create app directory
WORKDIR /app

# Copy application files
COPY youtube_downloader.py .

# Create directories for downloads and configs
RUN mkdir -p /downloads /config /logs

# Environment variables with defaults
ENV CONFIG_PATH=/config/videos.yaml
ENV DOWNLOAD_PATH=/downloads
ENV LOG_PATH=/logs
ENV JSON_OUTPUT=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Run as non-root user for security
RUN useradd -m -u 1000 downloader && \
    chown -R downloader:downloader /app /downloads /config /logs
USER downloader

# Entry point script
COPY docker-entrypoint.sh /docker-entrypoint.sh
USER root
RUN chmod +x /docker-entrypoint.sh
USER downloader

ENTRYPOINT ["/docker-entrypoint.sh"]