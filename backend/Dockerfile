# === Backend ===
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias del proyecto principal
COPY requirements.txt /app/requirements.txt

# Instalar dependencias
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar TODO el proyecto (backend, src, utils, etc.)
COPY . /app

# Asegurar que el backend sea accesible desde cualquier módulo
ENV PYTHONPATH="/app"

# Exponer el puerto del backend
EXPOSE 8000

# Comando de arranque de FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
