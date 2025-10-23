import streamlit as st
import requests
import time

# --- Configuración inicial ---
st.set_page_config(
    page_title="ChatBot IA - Universidad de Caldas",
    page_icon="🤖",
    layout="centered"
)

API_URL = "http://api:8000/query"  # Backend del contenedor Docker

# --- Encabezado principal ---
st.markdown(
    """
    <h1 style='text-align: center; color: #3A9AD9;'>🤖 ChatBot IA - Universidad de Caldas</h1>
    <p style='text-align: center; color: #374151;'>
        Aprende sobre <b>Inteligencia Artificial</b> con un asistente académico.  
        Pregunta sobre <i>conceptos, historia, aprendizaje automático, ética o regulaciones.</i>
    </p>
    """,
    unsafe_allow_html=True
)

# --- Contenedor principal tipo chat ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Selector de modo ---
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("💬 Escribe tu pregunta:")
with col2:
    mode = st.selectbox("Modo", ["breve", "extendido"])

# --- Botón de envío ---
if st.button("🚀 Enviar pregunta"):
    if not question.strip():
        st.warning("Por favor, escribe una pregunta.")
    else:
        with st.spinner("Pensando... ⏳"):
            start = time.time()
            try:
                response = requests.post(API_URL, json={"question": question, "mode": mode})
                latency = round(time.time() - start, 2)

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No se pudo generar una respuesta.")
                    citations = data.get("citations", [])

                    st.session_state.history.append({
                        "question": question,
                        "answer": answer,
                        "citations": citations,
                        "latency": latency
                    })
                else:
                    st.error(f"❌ Error del servidor ({response.status_code})")
            except Exception as e:
                st.error(f"⚠️ Error al conectar con el backend: {e}")

# --- Mostrar historial ---
if st.session_state.history:
    st.markdown("## 💬 Historial de conversación")
    for i, item in enumerate(reversed(st.session_state.history)):
        st.markdown(f"**🧑‍🎓 Tú:** {item['question']}")
        st.markdown(f"**🤖 ChatBot:** {item['answer']}")
        st.caption(f"⏱️ {item['latency']} s | Modo: {mode}")
        if item["citations"]:
            with st.expander("📚 Fuentes citadas"):
                for c in item["citations"]:
                    st.markdown(f"- {c}")
        st.markdown("---")

# --- Barra lateral ---
st.sidebar.header("ℹ️ Información")
st.sidebar.info(
    """
    **Proyecto académico** desarrollado por:
    - Heidy 🧩  
    - Julián 💡  
    - Edwar ⚙️ *(Líder técnico - Infra & MLOps)*  

    ---
    💻 **Stack:** FastAPI + Streamlit + Docker  
    📊 Monitoreo: métricas, logs anonimizados  
    🔐 Seguridad: variables .env y control local
    """
)

st.sidebar.markdown("---")
st.sidebar.write("Universidad de Caldas © 2025")
