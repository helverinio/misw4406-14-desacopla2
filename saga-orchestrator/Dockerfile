FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management
RUN pip install uv

# Copy dependency files and README (needed for package metadata)
COPY pyproject.toml ./
COPY uv.lock* ./
COPY README.md ./

# Install dependencies without installing the package itself
RUN if [ -f uv.lock ]; then uv sync --frozen --no-install-project; else uv sync --no-install-project; fi

# Copy application code
COPY . .

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5003

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/health || exit 1

# Run the application
CMD ["uv", "run", "python", "app.py"]
