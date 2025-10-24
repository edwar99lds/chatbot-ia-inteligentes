import os
from dotenv import load_dotenv
from transformers import pipeline
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI, AuthenticationError, RateLimitError
import torch

load_dotenv()

# =====================================================
# 🔹 Función para obtener el modelo LLM (OpenAI o local)
# =====================================================
def get_llm(force_local=False):
    """Devuelve un modelo LLM remoto (OpenAI) o local (Flan-T5)."""
    if not force_local:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from langchain_openai import OpenAI as LCOpenAI
                print("✅ Intentando usar modelo remoto: gpt-3.5-turbo-instruct")
                client = OpenAI(api_key=api_key)
                client.models.list()
                print("🔐 Conexión con OpenAI exitosa.")
                return LCOpenAI(
                    model_name="gpt-3.5-turbo-instruct",
                    temperature=0.2,
                    api_key=api_key
                )
            except (AuthenticationError, RateLimitError):
                print("⚠️ Error de autenticación o cuota agotada, usando modelo local.")
            except Exception as e:
                print(f"⚠️ No se pudo conectar a OpenAI: {e}")

    # 🔸 Si no hay API key o hay error → usar modelo local con FLAN-T5
    print("💻 Usando modelo local gratuito: google/flan-t5-small (Hugging Face)")

    # Ajustar número de threads para CPU (puedes bajarlo si tu CPU es débil)
    torch.set_num_threads(4)

    # Cargar modelo local de texto a texto (instruccional)
    local_model = pipeline(
        "text2text-generation",
        model="google/flan-t5-base",
        device_map=None,  # CPU
        torch_dtype=torch.float32
    )

    class LocalLLM:
        def invoke(self, prompt):
            try:
                output = local_model(
                    prompt,
                    max_new_tokens=200,
                    do_sample=False
                )[0]["generated_text"]
                return f"(Respuesta local)\n{output.strip()}"
            except Exception as e:
                return f"[Error al generar con modelo local: {e}]"

    return LocalLLM()

# =====================================================
# 🔹 Construcción del pipeline RAG
# =====================================================
def get_rag_chain():
    """Crea el pipeline RAG con embeddings y retrieval."""
    print("🔹 Cargando base vectorial...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory="data/chroma_db", embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_template(
        """Usa la siguiente información para responder la pregunta del usuario.
Si no encuentras la respuesta, di "No tengo información suficiente".
Incluye siempre las fuentes entre paréntesis.

Contexto:
{context}

Pregunta:
{question}

Respuesta:"""
    )

    llm = get_llm()

    def safe_invoke(question):
        try:
            chain = (
                RunnableParallel({
                    "context": retriever,
                    "question": RunnablePassthrough()
                })
                | prompt
                | llm
                | StrOutputParser()
            )
            return chain.invoke(question)

        except RateLimitError:
            print("⚠️ Límite de uso alcanzado, cambiando a modelo local definitivo...")
            local_llm = get_llm(force_local=True)
            context_docs = retriever.invoke(question)
            context = "\n\n".join([d.page_content for d in context_docs])
            context = context[:1500]  # Limita el contexto a 1500 caracteres (~400 tokens)
            prompt_text = prompt.format(context=context, question=question)
            return local_llm.invoke(prompt_text)

        except Exception as e:
            return f"[Error al procesar la pregunta: {e}]"

    return safe_invoke

# =====================================================
# 🔹 Prueba directa del pipeline
# =====================================================
if __name__ == "__main__":
    question = "¿Qué es el aprendizaje profundo?"
    print("❓ Pregunta:", question)
    chain = get_rag_chain()
    answer = chain(question)
    print("\n💬 Respuesta:\n", answer)
