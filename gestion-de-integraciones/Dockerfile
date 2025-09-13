FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema y uv
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copiar archivos de configuración
COPY pyproject.toml .
COPY requirements.txt .
COPY README.md .

# Instalar dependencias con uv
RUN uv sync --no-dev

# Copiar código fuente
COPY . .

# Exponer puerto
EXPOSE 5001

# Variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app:/app/gestion_de_integraciones

# Comando para ejecutar la aplicación
CMD ["uv", "run", "python", "app.py"]
