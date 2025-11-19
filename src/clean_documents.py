# src/clean_documents.py
import os
import re
import fitz  # PyMuPDF

RAW_DOCS_DIR = "data/docs"
CLEAN_DOCS_DIR = "data/clean_docs"

os.makedirs(CLEAN_DOCS_DIR, exist_ok=True)

def clean_text(text):
    """Limpia el texto extraído de los PDFs."""
    text = re.sub(r'\n+', '\n', text)          # Quita saltos de línea consecutivos
    text = re.sub(r'\s{2,}', ' ', text)        # Reemplaza múltiples espacios por uno
    text = re.sub(r'Página\s*\d+', '', text)   # Elimina numeraciones de página
    text = re.sub(r'[^a-zA-Z0-9ÁÉÍÓÚáéíóúñÑ.,;:()¿?¡!%$#@/\-\s]', '', text)  # Limpieza de símbolos raros
    text = text.strip()
    return text

def clean_pdfs():
    for filename in os.listdir(RAW_DOCS_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(RAW_DOCS_DIR, filename)
            print(f"🧹 Procesando: {filename}")

            doc = fitz.open(file_path)
            full_text = ""

            # Extraer texto página por página
            for page in doc:
                page_text = page.get_text("text")
                full_text += page_text + "\n"

            doc.close()

            # Limpiar el texto
            clean = clean_text(full_text)

            # Guardar como archivo .txt limpio
            clean_filename = os.path.splitext(filename)[0] + ".txt"
            clean_path = os.path.join(CLEAN_DOCS_DIR, clean_filename)
            with open(clean_path, "w", encoding="utf-8") as f:
                f.write(clean)

            print(f"✅ Documento limpio guardado en: {clean_path}")

if __name__ == "__main__":
    clean_pdfs()
