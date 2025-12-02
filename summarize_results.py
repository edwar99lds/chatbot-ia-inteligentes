# summarize_results.py
import csv
import os
import glob
import argparse
import statistics
from datetime import datetime

LOGS_DIR = "logs"
SCORED_GLOB = os.path.join(LOGS_DIR, "evaluation_scored_*.csv")

# ----------------- Utils -----------------

def pick_input_file(explicit_path: str | None) -> str:
    """Devuelve la ruta del CSV a resumir.
       - Si se pasa --in, usa esa ruta.
       - Si no, toma el evaluation_scored_*.csv más reciente en logs/.
    """
    if explicit_path:
        if not os.path.exists(explicit_path):
            raise FileNotFoundError(f"No existe el archivo especificado: {explicit_path}")
        return explicit_path

    files = sorted(glob.glob(SCORED_GLOB), key=os.path.getmtime, reverse=True)
    if not files:
        legacy = os.path.join(LOGS_DIR, "evaluation_scored.csv")
        if os.path.exists(legacy):
            return legacy
        raise FileNotFoundError(
            "No se encontraron archivos 'evaluation_scored_*.csv' en logs/. "
            "Ejecuta enrich_results.py primero, o pasa la ruta con --in"
        )
    return files[0]

def derive_suffix(in_path: str) -> str:
    """Extrae el sufijo timestamp del archivo de entrada si existe."""
    base = os.path.basename(in_path)
    if base.startswith("evaluation_scored_") and base.endswith(".csv"):
        return base[len("evaluation_scored_") : -len(".csv")]
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def to_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def to_int(x, default=0):
    try:
        return int(float(x))
    except Exception:
        return default

def mean_or_0(vals):
    try:
        return round(statistics.mean(vals), 3) if vals else 0.0
    except statistics.StatisticsError:
        return 0.0

def median_or_0(vals):
    try:
        return round(statistics.median(vals), 3) if vals else 0.0
    except statistics.StatisticsError:
        return 0.0

def pctl(vals, p):
    if not vals:
        return 0.0
    s = sorted(vals)
    k = int(round((p/100.0)*(len(s)-1)))
    return round(s[k], 3)

def group_by(rows, key):
    out = {}
    for r in rows:
        k = r.get(key, "desconocido")
        out.setdefault(k, []).append(r)
    return out

# ----------------- Summary builders -----------------

def summarize_block(items):
    lat = [to_float(r.get("latencia", 0)) for r in items]
    acc = [to_float(r.get("exactitud", 0)) for r in items]
    cov = [to_float(r.get("cobertura", 0)) for r in items]
    cla = [to_float(r.get("claridad", 0)) for r in items]
    cit = [to_float(r.get("cita_valida", 0)) for r in items]
    alu = [to_float(r.get("alucinacion", 0)) for r in items]
    seg = [to_float(r.get("seguridad", 0)) for r in items]
    scr = [to_float(r.get("score_r", 0)) for r in items]

    return {
        "n_preguntas": len(items),
        "latencia_prom": mean_or_0(lat),
        "latencia_mediana": median_or_0(lat),
        "latencia_p90": pctl(lat, 90),
        "exactitud_prom": mean_or_0(acc),
        "cobertura_prom": mean_or_0(cov),
        "claridad_prom(1-5)": mean_or_0(cla),
        "cita_valida_%": round(mean_or_0(cit)*100, 1),
        "alucinacion_%": round(mean_or_0(alu)*100, 1),
        "seguridad_%": round(mean_or_0(seg)*100, 1),
        "score_r_prom": mean_or_0(scr),
        "score_r_mediana": median_or_0(scr),
        "score_r_p90": pctl(scr, 90),
    }

# ----------------- Main -----------------

def main():
    parser = argparse.ArgumentParser(description="Resumen de resultados enriquecidos.")
    parser.add_argument("--in", dest="in_path", default=None, help="Ruta del CSV evaluation_scored_*.csv (opcional)")
    args = parser.parse_args()

    in_path = pick_input_file(args.in_path)
    suffix = derive_suffix(in_path)

    print(f"📥 Leyendo:  {in_path}")
    with open(in_path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError("El archivo de entrada no tiene filas.")

    # asegurar modelo/categoria/tipo_pregunta por compatibilidad
    for r in rows:
        r.setdefault("modelo", "desconocido")
        r.setdefault("categoria", "desconocido")
        r.setdefault("tipo_pregunta", "desconocido")

    # ---- Summary overall por modelo ----
    by_model = group_by(rows, "modelo")
    summary_overall = []
    for model, items in by_model.items():
        s = summarize_block(items)
        s["modelo"] = model
        summary_overall.append(s)

    # ---- Summary por categoría y tipo_pregunta ----
    # (1) por categoría
    by_cat = group_by(rows, "categoria")
    summary_by_cat = []
    for cat, items in by_cat.items():
        s = summarize_block(items)
        s["categoria"] = cat
        summary_by_cat.append(s)

    # (2) por tipo_pregunta
    by_tipo = group_by(rows, "tipo_pregunta")
    summary_by_tipo = []
    for t, items in by_tipo.items():
        s = summarize_block(items)
        s["tipo_pregunta"] = t
        summary_by_tipo.append(s)

    # ---- Top peores / mejores (global por score_r) ----
    scored = [r for r in rows if r.get("score_r") not in (None, "", "nan")]
    for r in scored:
        r["score_r"] = to_float(r.get("score_r", 0))
    scored.sort(key=lambda x: x["score_r"])
    worst = scored[:10]
    best = list(reversed(scored))[:10]

    # ---- Write outputs ----
    os.makedirs(LOGS_DIR, exist_ok=True)
    out_overall = os.path.join(LOGS_DIR, f"summary_overall_{suffix}.csv")
    out_by_cat  = os.path.join(LOGS_DIR, f"summary_by_category_{suffix}.csv")
    out_by_tipo = os.path.join(LOGS_DIR, f"summary_by_tipo_{suffix}.csv")
    out_worst   = os.path.join(LOGS_DIR, f"top_peores_{suffix}.csv")
    out_best    = os.path.join(LOGS_DIR, f"top_mejores_{suffix}.csv")

    # overall
    with open(out_overall, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["modelo","n_preguntas","latencia_prom","latencia_mediana","latencia_p90",
                      "exactitud_prom","cobertura_prom","claridad_prom(1-5)",
                      "cita_valida_%","alucinacion_%","seguridad_%",
                      "score_r_prom","score_r_mediana","score_r_p90"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_overall)

    # by category
    with open(out_by_cat, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["categoria","n_preguntas","latencia_prom","latencia_mediana","latencia_p90",
                      "exactitud_prom","cobertura_prom","claridad_prom(1-5)",
                      "cita_valida_%","alucinacion_%","seguridad_%",
                      "score_r_prom","score_r_mediana","score_r_p90"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_by_cat)

    # by tipo
    with open(out_by_tipo, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["tipo_pregunta","n_preguntas","latencia_prom","latencia_mediana","latencia_p90",
                      "exactitud_prom","cobertura_prom","claridad_prom(1-5)",
                      "cita_valida_%","alucinacion_%","seguridad_%",
                      "score_r_prom","score_r_mediana","score_r_p90"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_by_tipo)

    # worst / best
    if worst:
        with open(out_worst, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=worst[0].keys())
            writer.writeheader()
            writer.writerows(worst)
    if best:
        with open(out_best, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=best[0].keys())
            writer.writeheader()
            writer.writerows(best)

    print(f"✅ Resumen por modelo → {out_overall}")
    print(f"✅ Resumen por categoría → {out_by_cat}")
    print(f"✅ Resumen por tipo → {out_by_tipo}")
    print(f"✅ Top peores → {out_worst}")
    print(f"✅ Top mejores → {out_best}")

if __name__ == "__main__":
    main()
