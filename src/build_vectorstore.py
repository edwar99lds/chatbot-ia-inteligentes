# src/build_vectorstore.py
import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def build_vectorstore():
    print("📄 Cargando documentos desde: data/docs")
    loader = DirectoryLoader("data/docs", glob="*.pdf", loader_cls=PyPDFLoader)
    docs = loader.load()

    if not docs:
        raise ValueError("⚠️ No se encontraron documentos PDF en data/docs")

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
