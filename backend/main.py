# ===========================================
# 🧠 Backend del ChatBot IA – Universidad de Caldas
# Autor: Edwar Marín
# Rol: Infraestructura & MLOps
# ===========================================

from fastapi import FastAPI
from pydantic import BaseModel
import time
import os
from dotenv import load_dotenv

# --- Importaciones locales ---
from utils.logger import log_interaction   # 📊 Registro de métricas
from src.rag_pipeline import get_rag_chain          # 🔗 Pipeline RAG real

# =====================================================
# 🔹 Cargar variables de entorno
# =====================================================
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PATH = os.getenv("DB_PATH", "data/vectorstore")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

if DEBUG:
    print(f"🔐 OPENAI_API_KEY: {OPENAI_API_KEY[:5]}******" if OPENAI_API_KEY else "🔐 No hay API Key configurada.")
    print(f"🗂️ DB_PATH: {DB_PATH}")
    print(f"🐞 DEBUG mode: {DEBUG}")

# =====================================================
# 🔹 Inicializar FastAPI
# =====================================================
app = FastAPI(
    title="ChatBot IA - Backend",
    description="Backend para ChatBot académico sobre Inteligencia Artificial",
    version="1.0"
)

# =====================================================
# 🔹 Inicializar el pipeline RAG
# =====================================================
print("🧠 Inicializando pipeline RAG...")
rag_chain = get_rag_chain()
print("✅ RAG cargado y listo.")

# =====================================================
# 🔹 Modelos de datos
# =====================================================
class QueryRequest(BaseModel):
    question: str
    mode: str  # "breve" o "extendido"

# =====================================================
# 🔹 Rutas del backend
# =====================================================

@app.get("/")
def read_root():
    """Ruta de prueba del servidor."""
    return {"message": "Bienvenido al backend del ChatBot de IA - Universidad de Caldas"}


@app.post("/query")
def get_answer(request: QueryRequest):
    """
    Responde a la pregunta del usuario usando el pipeline RAG.
    Registra métricas de latencia y uso en logs/metrics.jsonl
    """
    start_time = time.time()

    try:
        # --- Ejecutar el pipeline RAG ---
        print(f"🤖 Pregunta recibida: {request.question}")
        answer_text = rag_chain(request.question)
        latency = time.time() - start_time

        # --- Citas simuladas (puedes sustituirlas si tu RAG las genera) ---
        citations = ["Base vectorial académica - Universidad de Caldas"]

        # --- Registrar métricas ---
        log_interaction(
            question=request.question,
            model="RAG (OpenAI + FLAN-T5)",
            latency=latency,
            cost=0.0  # sin costo real por ahora
        )

        return {
            "answer": answer_text,
            "citations": citations
        }

    except Exception as e:
        print(f"❌ Error en RAG: {e}")
        return {
            "answer": f"[Error interno del RAG: {str(e)}]",
            "citations": []
        }

# =====================================================
# 🧩 Instrucciones de ejecución
# =====================================================
# Modo desarrollo:
#   python -m uvicorn backend.main:app --reload --port 8000
#
# Docker:
#   docker compose up --build
#
# Logs:
#   Se guardan en logs/metrics.jsonl
#
# =====================================================


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
