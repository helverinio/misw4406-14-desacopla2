FROM python:3.11.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev pkg-config \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements primero (para cacheo)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar solo el código fuente
COPY ./src ./src

# Exponer puerto
EXPOSE 8000

# Comando de arranque: ejecutar script antes de arrancar Uvicorn
CMD ["sh", "-c", "python -m uvicorn src.presentation.api.main:app --host 0.0.0.0 --port 8000 --reload"]
