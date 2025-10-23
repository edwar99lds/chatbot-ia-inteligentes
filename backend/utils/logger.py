import time
import uuid
import json
from datetime import datetime
import os

# Crear carpeta logs si no existe
os.makedirs("logs", exist_ok=True)

def log_interaction(question, model, latency, cost):
    """
    Registra información de cada consulta sin almacenar datos sensibles.
    Guarda los datos en formato JSONL (una línea por evento).
    """
    entry = {
        "session_id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "question_length": len(question),
        "model": model,
        "latency_ms": round(latency * 1000, 2),
        "cost_usd": round(cost, 5)
    }

    with open("logs/metrics.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
