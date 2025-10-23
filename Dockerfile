# Dockerfile (para el frontend)
FROM python:3.11

WORKDIR /app

# Copiar el código de la app y dependencias
COPY app_streamlit.py /app
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de Streamlit
EXPOSE 8501

# Comando para ejecutar Streamlit
CMD ["streamlit", "run", "app_streamlit.py", "--server.port=8501", "--server.address=0.0.0.0"]
