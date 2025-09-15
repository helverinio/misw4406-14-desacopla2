FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
#COPY uv.lock ./
# (Si no traes uv.lock) créalo dentro del contenedor:
RUN uv lock
COPY README.md ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy source code
COPY src/ ./src/

# Expose port
EXPOSE 5004

# Run the application
CMD ["uv", "run", "flask", "--app", "src.alpespartners.api_compliance:create_app", "run", "--host=0.0.0.0", "--port=5004"]