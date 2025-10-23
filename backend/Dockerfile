# backend/Dockerfile
FROM python:3.11

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiamos los archivos del backend y el requirements
COPY ./backend /app
COPY requirements.txt .

# Instalamos dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponemos el puerto 8000
EXPOSE 8000

# Comando por defecto para correr la API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
