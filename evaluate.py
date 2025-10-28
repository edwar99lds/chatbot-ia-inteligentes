# evaluate.py
import csv
import requests
import time
import os
from evaluate_metrics import (
    evaluar_exactitud,
    evaluar_cobertura,
    evaluar_claridad,
    detectar_alucinacion,
    detectar_cita_valida
)

API_URL = "http://localhost:8000/query"

print("🚀 Iniciando evaluación automática del ChatBot IA...")
print(f"Consultando endpoint: {API_URL}")

data_path = "data/gold_questions.csv"
output_path = "logs/evaluation_results.csv"

if not os.path.exists(data_path):
    print(f"⚠️ No se encontró el archivo {data_path}")
    exit(1)

results = []

with open(data_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        pregunta = row["pregunta"]
        respuesta_esperada = row["respuesta_esperada"]

        start = time.time()
        try:
            r = requests.post(API_URL, json={"question": pregunta, "mode": "breve"})
            latency = round(time.time() - start, 3)

            if r.status_code == 200:
                data = r.json()
                respuesta_modelo = data.get("answer", "")
                citations = len(data.get("citations", []))

                # Evaluación automática
                exactitud = evaluar_exactitud(respuesta_modelo, respuesta_esperada)
                conceptos_clave = [w.strip('.,') for w in respuesta_esperada.split() if len(w) > 3]
                cobertura = evaluar_cobertura(respuesta_modelo, conceptos_clave)
                claridad = evaluar_claridad(respuesta_modelo)
                alucinacion = detectar_alucinacion(respuesta_modelo)
                cita_valida = detectar_cita_valida(respuesta_modelo)

                results.append({
                    "pregunta": pregunta,
                    "respuesta_esperada": respuesta_esperada,
                    "respuesta_modelo": respuesta_modelo,
                    "latencia": latency,
                    "citaciones": citations,
                    "exactitud": exactitud,
                    "cobertura": cobertura,
                    "claridad": claridad,
                    "alucinacion": alucinacion,
                    "cita_valida": cita_valida,
                    "estado": "OK"
                })

            else:
                results.append({
                    "pregunta": pregunta,
                    "respuesta_esperada": respuesta_esperada,
                    "respuesta_modelo": "",
                    "latencia": latency,
                    "citaciones": 0,
                    "exactitud": 0,
                    "cobertura": 0,
                    "claridad": 0,
                    "alucinacion": 1,
                    "cita_valida": 0,
                    "estado": f"Error {r.status_code}"
                })

        except Exception as e:
            results.append({
                "pregunta": pregunta,
                "respuesta_esperada": respuesta_esperada,
                "respuesta_modelo": "",
                "latencia": 0,
                "citaciones": 0,
                "exactitud": 0,
                "cobertura": 0,
                "claridad": 0,
                "alucinacion": 1,
                "cita_valida": 0,
                "estado": f"Fail: {e}"
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
