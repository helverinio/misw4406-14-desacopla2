FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/src

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Create non-root user
RUN addgroup --system appuser && adduser --system --group --home /home/appuser appuser

# Create cache directory for uv in user's home directory
RUN mkdir -p /home/appuser/.cache/uv && \
    chown -R appuser:appuser /home/appuser

# Copy project files
COPY pyproject.toml .
COPY uv.lock .
COPY README.md .

# Install dependencies using uv
RUN uv sync --locked --no-dev

# Copy source code
COPY src ./src

# Set ownership of app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 5000

# Run the application
CMD ["flask", "--app", "src.alpespartners.api:create_app", "run", "--host=0.0.0.0", "--port=5000"]
