import json

def analyze_logs(file_path="logs/metrics.jsonl"):
    with open(file_path, "r", encoding="utf-8") as f:
        entries = [json.loads(line) for line in f.readlines()]

    total = len(entries)
    avg_latency = sum(e["latency_ms"] for e in entries) / total
    avg_question_len = sum(e["question_length"] for e in entries) / total
    total_cost = sum(e["cost_usd"] for e in entries)

    print(f"📊 Total de consultas: {total}")
    print(f"⏱ Latencia promedio: {avg_latency:.2f} ms")
    print(f"📝 Longitud promedio de pregunta: {avg_question_len:.1f} caracteres")
    print(f"💰 Costo total estimado: ${total_cost:.5f}")

if __name__ == "__main__":
    analyze_logs()
