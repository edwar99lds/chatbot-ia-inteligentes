# src/build_vectorstore.py
import os
from langchain_community.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_vectorstore():
    print("📄 Cargando documentos desde: data/clean_docs")
    docs = []

    clean_dir = "data/clean_docs"
    for filename in os.listdir(clean_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(clean_dir, filename)
            print(f"📚 Leyendo {filename}...")

            # Intentar leer el archivo en UTF-8, ignorando caracteres inválidos
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

            docs.append(Document(page_content=text, metadata={"source": filename}))

    if not docs:
        raise ValueError("⚠️ No se encontraron documentos TXT en data/clean_docs")

    print("✂️ Dividiendo documentos en fragmentos...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    print("🔢 Generando embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("💾 Construyendo base vectorial en: data/chroma_db")
    vectordb = Chroma.from_documents(chunks, embedding=embeddings, persist_directory="data/chroma_db")

    print("✅ Base vectorial creada exitosamente.")


if __name__ == "__main__":
    build_vectorstore()
