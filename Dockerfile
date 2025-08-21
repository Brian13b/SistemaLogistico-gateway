FROM python:3.11-slim

# Instala herramientas necesarias para compilar paquetes nativos (como pydantic-core)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    rustc \
    cargo \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto
WORKDIR /
COPY . .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

