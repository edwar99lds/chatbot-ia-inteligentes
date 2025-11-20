import csv
import requests
import time
import os
import json
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
dump_invalid_json = True  # deja True para inspeccionar payloads problemáticos

if not os.path.exists(data_path):
    print(f"⚠️ No se encontró el archivo {data_path}")
    exit(1)

# ----------------- Utilidades -----------------

INSTRUCTION_HINTS = [
    "(respuesta local)",
    "human:",
    "system:",
    "usa la siguiente información",
    "di \"no tengo información suficiente\"",
    "di \"no tengo informacion suficiente\"",
]

PREFERRED_KEYS = [
    # orden de preferencia para strings de respuesta
    "answer", "output_text", "output", "text", "response", "result", "content"
]

def es_instruccion(texto: str) -> bool:
    t = (texto or "").strip()
    if not t:
        return True
    low = t.lower()
    return any(h in low for h in INSTRUCTION_HINTS)

def sanitize(texto: str) -> str:
    """
    Quita encabezados de instrucción y trata de extraer el bloque del 'assistant'
    si aparece dentro del mismo string.
    """
    if not isinstance(texto, str):
        return ""
    t = texto.strip()

    # Si viene todo el prompt concatenado, intenta cortar después de 'Assistant:' / 'Asistente:'
    for marker in ["\nAssistant:", "\nAsistente:", "\nassistant:", "\nRespuesta:", "\nModelo:"]:
        if marker in t:
            t = t.split(marker, 1)[1].strip()
            break

    # Elimina líneas que empiezan con etiquetas típicas
    lines = [ln for ln in t.splitlines() if not ln.strip().lower().startswith(("human:", "system:", "(respuesta local)"))]
    t2 = "\n".join(lines).strip()

    # Si lo saneado quedó vacío o sigue pareciendo instrucción, devolvemos cadena vacía
    if not t2 or es_instruccion(t2):
        return ""
    return t2

def _iter_strings(obj):
    """Itera recursivamente TODAS las cadenas encontradas en un objeto JSON."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)

def _get_by_path(dct, path_list):
    """Intenta obtener un valor por una ruta (lista de claves/índices) sin lanzar excepción."""
    cur = dct
    for key in path_list:
        try:
            if isinstance(key, int) and isinstance(cur, list):
                cur = cur[key]
            elif isinstance(cur, dict):
                cur = cur.get(key)
            else:
                return None
        except Exception:
            return None
    return cur

def extraer_respuesta(data: dict) -> str:
    """
    Busca la respuesta en varias rutas conocidas y, si no aparece,
    hace una búsqueda recursiva por claves preferidas.
    """
    if not isinstance(data, dict):
        return ""

    # 1) Rutas directas más comunes
    candidates = []

    # answer directo
    val = data.get("answer")
    if isinstance(val, str) and val.strip():
        candidates.append(val)

    # output.answer
    val = _get_by_path(data, ["output", "answer"])
    if isinstance(val, str) and val.strip():
        candidates.append(val)

    # OpenAI-style: choices[0].message.content
    val = _get_by_path(data, ["choices", 0, "message", "content"])
    if isinstance(val, str) and val.strip():
        candidates.append(val)

    # messages role=assistant
    msgs = data.get("messages")
    if isinstance(msgs, list):
        for m in msgs[::-1]:
            if isinstance(m, dict) and m.get("role") == "assistant":
                cont = m.get("content")
                if isinstance(cont, str) and cont.strip():
                    candidates.append(cont)
                    break

    # 2) Búsqueda por claves preferidas en cualquier profundidad (como 'content', 'text', etc.)
    if not candidates:
        for s in _iter_strings(data):
            # preferir strings que contengan contenido tipo oración
            # y excluir muy cortos
            st = s.strip()
            if len(st) >= 8:
                # si contiene marcas del assistant dentro, es prometedor
                if any(tag in st for tag in ["Assistant:", "Asistente:", "assistant:", "Respuesta:"]):
                    candidates.append(st)

        # si aún vacío, agrega strings por claves preferidas
        if not candidates:
            def key_score(s):
                low = s.lower()
                for i, k in enumerate(PREFERRED_KEYS):
                    if k in low:
                        return i
                return 999

            all_strings = list(_iter_strings(data))
            # Ordena por si menciona alguna 'preferred key'
            all_strings.sort(key=key_score)
            for s in all_strings:
                st = s.strip()
                if len(st) >= 12:
                    candidates.append(st)
                    if len(candidates) >= 3:
                        break

    # 3) Sanear y elegir la primera que parezca respuesta
    for c in candidates:
        cleaned = sanitize(c)
        if cleaned:
            return cleaned

    # 4) Si ninguna saneada sirve, devolver primera candidata no vacía (aunque luego la marcaremos como inválida)
    for c in candidates:
        if c and isinstance(c, str) and c.strip():
            return c.strip()

    return ""

def contar_citas(data: dict) -> int:
    try:
        cits = data.get("citations", [])
        if isinstance(cits, list):
            return len(cits)
        return 0
    except Exception:
        return 0

# ----------------- Evaluación -----------------

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

                respuesta_modelo = extraer_respuesta(data)
                citations = contar_citas(data)

                # dump JSON crudo si detectamos instrucción/no-respuesta
                mark_invalid = es_instruccion(respuesta_modelo) or not respuesta_modelo.strip()
                if mark_invalid and dump_invalid_json:
                    os.makedirs("logs/raw", exist_ok=True)
                    with open(f"logs/raw/debug_{int(time.time())}.json", "w", encoding="utf-8") as dbg:
                        json.dump(data, dbg, ensure_ascii=False, indent=2)

                if mark_invalid:
                    results.append({
                        "pregunta": pregunta,
                        "respuesta_esperada": respuesta_esperada,
                        "respuesta_modelo": respuesta_modelo,
                        "latencia": latency,
                        "citaciones": citations,
                        "exactitud": 0,
                        "cobertura": 0.0,
                        "claridad": 1,
                        "alucinacion": 1,
                        "cita_valida": 0,
                        "estado": "INVALID_ANSWER"
                    })
                    continue

                # evaluación normal
                exactitud = evaluar_exactitud(respuesta_modelo, respuesta_esperada)
                conceptos_clave = [w.strip('.,;:¡!¿?()"') for w in respuesta_esperada.split() if len(w) > 3]
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