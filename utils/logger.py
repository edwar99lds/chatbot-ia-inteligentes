# utils/logger.py
import os
import json
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "interactions.log")

def log_interaction(question: str, model: str, latency: float, cost: float):
    """Registra interacciones con el chatbot (para métricas y auditoría)."""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "model": model,
        "latency": round(latency, 3),
        "cost": cost
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
