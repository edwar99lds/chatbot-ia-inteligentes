# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
import time  # ⏱ Para medir latencia
from utils.logger import log_interaction  # 📊 Importa el registrador de métricas
from dotenv import load_dotenv
import os

# --- Cargar variables de entorno ---
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "data/vectorstore")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if DEBUG:
    print(f"🔐 OPENAI_API_KEY: {OPENAI_API_KEY[:5]}******")
    print(f"🗂️ DB_PATH: {DB_PATH}")
    print(f"🐞 DEBUG mode: {DEBUG}")

app = FastAPI(
    title="ChatBot IA - Backend",
    description="Backend para ChatBot académico sobre IA",
    version="1.0"
)

# Modelo de datos para la petición
class QueryRequest(BaseModel):
    question: str
    mode: str  # "breve" o "extendido"


# Ruta principal (saludo)
@app.get("/")
def read_root():
    return {"message": "Bienvenido al backend del ChatBot de IA - Universidad de Caldas"}


# Ruta de consulta
@app.post("/query")
def get_answer(request: QueryRequest):
    """
    Responde con un texto simulado y un par de citas de ejemplo.
    Luego aquí se integrará el pipeline RAG real.
    También registra métricas de uso (anonimizadas).
    """
    start_time = time.time()  # Inicia el contador de latencia

    # --- Simulación de respuesta (dummy) ---
    answer_text = (
        f"Hola 👋, soy el backend del ChatBot IA. "
        f"Tu pregunta fue: '{request.question}'. "
        f"Estoy en modo '{request.mode}'."
    )

    citations = [
        "UNESCO - Informe de Ética en IA 2023",
        "AI Act - Regulación Europea de IA 2024"
    ]

    # --- Cálculo de métricas ---
    latency = time.time() - start_time  # Latencia en segundos
    cost = 0.0003  # 💰 costo simbólico (simulación de uso de modelo)
    model_name = "mock-model-v1"

    # --- Registro en logs ---
    log_interaction(
        question=request.question,
        model=model_name,
        latency=latency,
        cost=cost
    )

    # --- Respuesta ---
    return {
        "answer": answer_text,
        "citations": citations
    }

# Backend - Terminal de visual
# python -m uvicorn backend.main:app --reload --port 8000


# Backend - Terminal de visual
# python -m uvicorn backend.main:app --reload --port 8000

#Frontend (lo abrí en git bash here)
# source venv/Scripts/activate
# streamlit run app_streamlit.py

# Ejecutar el programa:
# docker compose up

# Parar el programa
# docker compose down

# si se cambian dependencias:
# docker-compose up --build

# cloudflared tunnel --url http://localhost:8501
# cloudflared tunnel --url http://localhost:8501 --name chatbot-edwar

# python evaluate.py


# pip freeze > requirements.txt
