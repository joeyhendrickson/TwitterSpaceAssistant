# Multi-user Audio Assistant Dockerfile
FROM python:3.11-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    libasound2-dev \
    libportaudio2 \
    libportaudiocpp0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start the application
CMD ["streamlit", "run", "dashboard_multiuser.py", "--server.port=8501", "--server.address=0.0.0.0"]
