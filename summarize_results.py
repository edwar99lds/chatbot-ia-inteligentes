import csv, statistics, os

IN_CSV = "logs/evaluation_scored.csv"   # o el que renombres por modelo
OUT_SUM = "logs/summary.csv"
OUT_BEST = "logs/top_mejores.csv"
OUT_WORST = "logs/top_peores.csv"

with open(IN_CSV, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# si no usas columna 'modelo', asigna uno por defecto
for r in rows:
    r.setdefault("modelo", "desconocido")

def mean_col(items, col):
    vals = []
    for it in items:
        try:
            vals.append(float(it.get(col, "")))
        except:
            pass
    return round(statistics.mean(vals), 3) if vals else 0.0

# resumen por modelo
by_model = {}
for r in rows:
    by_model.setdefault(r["modelo"], []).append(r)

summ = []
for model, items in by_model.items():
    summ.append({
        "modelo": model,
        "n_preguntas": len(items),
        "latencia_prom": mean_col(items, "latencia"),
        "exactitud_prom": mean_col(items, "exactitud"),
        "cobertura_prom": mean_col(items, "cobertura"),
        "claridad_prom(1-5)": mean_col(items, "claridad"),
        "cita_valida_%": round(mean_col(items, "cita_valida")*100, 1),
        "alucinacion_%": round(mean_col(items, "alucinacion")*100, 1),
        "score_r_prom": mean_col(items, "score_r"),
    })

os.makedirs("logs", exist_ok=True)
with open(OUT_SUM, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=summ[0].keys())
    writer.writeheader()
    writer.writerows(summ)

# top peores/mejores por score_r (global)
scored = [r for r in rows if r.get("score_r")]
scored.sort(key=lambda x: float(x["score_r"]))
worst = scored[:10]
best = list(reversed(scored))[:10]

with open(OUT_WORST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=worst[0].keys())
    writer.writeheader()
    writer.writerows(worst)

with open(OUT_BEST, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=best[0].keys())
    writer.writeheader()
    writer.writerows(best)

print(f"✅ Resumen por modelo → {OUT_SUM}")
print(f"✅ Top peores → {OUT_WORST}")
print(f"✅ Top mejores → {OUT_BEST}")