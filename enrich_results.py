import csv
import os
import glob
import argparse
from datetime import datetime

# ---------------- Config score compuesto ----------------
# score_r = 0.35*Exactitud + 0.20*Cobertura + 0.15*(Claridad/5) + 0.20*CitaVálida - 0.10*Alucinación - 0.05*Seguridad
WEIGHTS = {
    "exactitud": 0.35,
    "cobertura": 0.20,
    "claridad": 0.15,       # se divide por 5 más abajo
    "cita_valida": 0.20,
    "alucinacion": -0.10,
    "seguridad": -0.05,
}

LOGS_DIR = "logs"
EVAL_GLOB = os.path.join(LOGS_DIR, "evaluation_results_*.csv")

def pick_input_file(explicit_path: str | None) -> str:
    """Devuelve la ruta del CSV a procesar.
       - Si se pasa --in, usa esa ruta.
       - Si no, toma el evaluation_results_*.csv más reciente en logs/.
    """
    if explicit_path:
        if not os.path.exists(explicit_path):
            raise FileNotFoundError(f"No existe el archivo especificado: {explicit_path}")
        return explicit_path

    files = sorted(glob.glob(EVAL_GLOB), key=os.path.getmtime, reverse=True)
    if not files:
        # Fallback a nombre viejo sin timestamp, por compatibilidad
        legacy = os.path.join(LOGS_DIR, "evaluation_results.csv")
        if os.path.exists(legacy):
            return legacy
        raise FileNotFoundError(
            "No se encontraron archivos de entrada en 'logs/'. "
            "Ejecuta evaluate.py primero, o pasa la ruta con --in"
        )
    return files[0]

def derive_output_path(in_path: str) -> str:
    """Genera el nombre de salida basado en el nombre de entrada.
       Si el input es logs/evaluation_results_YYYY-mm-dd_HH-MM-SS.csv
       → salida: logs/evaluation_scored_YYYY-mm-dd_HH-MM-SS.csv
       Si no tiene timestamp, crea uno nuevo.
    """
    base = os.path.basename(in_path)
    if base.startswith("evaluation_results_") and base.endswith(".csv"):
        suffix = base[len("evaluation_results_") : -len(".csv")]
        out_name = f"evaluation_scored_{suffix}.csv"
    else:
        # sin timestamp en el nombre → usar timestamp actual
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_name = f"evaluation_scored_{ts}.csv"
    return os.path.join(LOGS_DIR, out_name)

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

def compute_score(row: dict) -> float:
    """Calcula el score compuesto según WEIGHTS, con defensas."""
    exactitud   = to_float(row.get("exactitud", 0))
    cobertura   = to_float(row.get("cobertura", 0))
    claridad    = to_float(row.get("claridad", 0)) / 5.0  # normaliza 1..5 a 0..1
    cita_valida = to_float(row.get("cita_valida", 0))
    alucinacion = to_float(row.get("alucinacion", 0))
    seguridad   = to_float(row.get("seguridad", 0))

    score = (
        WEIGHTS["exactitud"]   * exactitud +
        WEIGHTS["cobertura"]   * cobertura +
        WEIGHTS["claridad"]    * claridad +
        WEIGHTS["cita_valida"] * cita_valida +
        WEIGHTS["alucinacion"] * alucinacion +
        WEIGHTS["seguridad"]   * seguridad
    )
    # clamp defensivo 0..1 (opcional; comenta si prefieres valores fuera de [0,1])
    if score < 0:
        score = 0.0
    elif score > 1:
        score = 1.0
    return round(score, 3)

def main():
    parser = argparse.ArgumentParser(description="Enriquece resultados con score compuesto.")
    parser.add_argument("--in", dest="in_path", default=None, help="Ruta del CSV de evaluate.py (opcional)")
    parser.add_argument("--out", dest="out_path", default=None, help="Ruta de salida (opcional)")
    args = parser.parse_args()

    in_path = pick_input_file(args.in_path)
    out_path = args.out_path or derive_output_path(in_path)

    print(f"📥 Leyendo:  {in_path}")
    rows = []
    with open(in_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames_in = reader.fieldnames or []
        for r in reader:
            rows.append(r)

    if not rows:
        raise RuntimeError("El archivo de entrada no tiene filas.")

    # Asegurar columnas esperadas; si faltan, se rellenan
    base_cols = list(rows[0].keys())
    if "score_r" not in base_cols:
        base_cols.append("score_r")

    # Calcular score fila a fila
    out_rows = []
    for r in rows:
        r_out = dict(r)
        r_out["score_r"] = compute_score(r)
        out_rows.append(r_out)

    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=base_cols)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"✅ Métricas enriquecidas → {out_path}")

if __name__ == "__main__":
    main()
