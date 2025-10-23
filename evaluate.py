# evaluate.py
import csv
import requests
import time
import os

API_URL = "http://localhost:8000/query"  # endpoint del backend

# Asegura que el backend esté corriendo antes de ejecutar este script
print("🚀 Iniciando evaluación automática del ChatBot IA...")
print(f"Consultando endpoint: {API_URL}")

results = []

data_path = "data/gold_questions.csv"
output_path = "logs/evaluation_results.csv"

# Verifica existencia del archivo de entrada
if not os.path.exists(data_path):
    print(f"⚠️ No se encontró el archivo {data_path}")
    exit(1)

with open(data_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = row["question"]
        start = time.time()
        try:
            r = requests.post(API_URL, json={"question": q, "mode": "breve"})
            latency = round(time.time() - start, 3)
            if r.status_code == 200:
                data = r.json()
                results.append({
                    "question": q,
                    "latency": latency,
                    "answer": data.get("answer", ""),
                    "citations": len(data.get("citations", [])),
                    "status": "OK"
                })
            else:
                results.append({
                    "question": q,
                    "latency": latency,
                    "answer": "",
                    "citations": 0,
                    "status": f"Error {r.status_code}"
                })
        except Exception as e:
            results.append({
                "question": q,
                "latency": 0,
                "answer": "",
                "citations": 0,
                "status": f"Fail: {e}"
            })

# Guardar resultados
if results:
    os.makedirs("logs", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"✅ Evaluación completada. Resultados guardados en: {output_path}")
else:
    print("⚠️ No se generaron resultados. Verifica que el backend esté corriendo.")
