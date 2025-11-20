import csv, os
from evaluate_metrics import (
    evaluar_exactitud, evaluar_cobertura, evaluar_claridad,
    detectar_alucinacion, detectar_cita_valida
)

IN_GOLD = "data/gold_questions.csv"
IN_RESULTS = "logs/evaluation_results.csv"     # cámbialo si usas el renombrado por modelo
OUT_SCORED = "logs/evaluation_scored.csv"

# indexar respuestas esperadas por pregunta
gold = {}
with open(IN_GOLD, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    # adapta a tus encabezados reales:
    key_q = "pregunta" if "pregunta" in reader.fieldnames else "question"
    key_ref = "respuesta_esperada" if "respuesta_esperada" in reader.fieldnames else "expected_answer"
    for r in reader:
        gold[r[key_q]] = r.get(key_ref, "")

rows = []
with open(IN_RESULTS, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fn = reader.fieldnames

    q_key = "question" if "question" in fn else "pregunta"
    a_key = "answer" if "answer" in fn else "respuesta_modelo"

    for r in reader:
        q = r.get(q_key, "")
        ans = r.get(a_key, "")
        expected = gold.get(q, "")

        # conceptos clave simples: palabras (>3 chars) de la esperada
        conceptos = [w.strip('.,;:¡!¿?()"') for w in expected.split() if len(w) > 3]

        exactitud = evaluar_exactitud(ans, expected)
        cobertura = evaluar_cobertura(ans, conceptos)
        claridad = evaluar_claridad(ans)
        alucinacion = detectar_alucinacion(ans)
        cita_valida = detectar_cita_valida(ans)

        # Score ponderado propuesto (ajústalo si tu profe dio otra fórmula)
        score_r = 0.35*exactitud + 0.20*cobertura + 0.15*(claridad/5.0) + 0.20*cita_valida - 0.10*alucinacion

        r_out = dict(r)
        r_out.update({
            "exactitud": exactitud,
            "cobertura": round(cobertura, 3),
            "claridad": claridad,
            "alucinacion": alucinacion,
            "cita_valida": cita_valida,
            "score_r": round(score_r, 3)
        })
        rows.append(r_out)

os.makedirs("logs", exist_ok=True)
with open(OUT_SCORED, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Métricas añadidas → {OUT_SCORED}")