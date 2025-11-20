import streamlit as st
import requests
import time

# --- Configuración inicial ---
st.set_page_config(
    page_title="ChatBot IA - Universidad de Caldas",
    page_icon="🤖",
    layout="wide"
)

API_URL = "http://api:8000/query"

# --- CSS personalizado ---
st.markdown("""
<style>

    /* ==== SIDEBAR - fondo azul oscuro + texto blanco ==== */
    [data-testid="stSidebar"] {
        background-color: #1E3A5F !important;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Aumentar margen superior del contenido del sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 30px !important;
    }

    /* ==== PANEL PRINCIPAL ==== */
    .main-title {
        color: #1E3A5F !important;
        text-align: center;
        font-weight: 800 !important;
        margin-top: -40px !important;
        margin-bottom: 5px !important;
    }

    .main-subtitle {
        color: #000000 !important;
        text-align: center;
        font-size: 18px;
        margin-top: -10px !important;
        margin-bottom: 25px !important;
    }

    /* Subir todo el contenedor de interacción */
    .block-container {
        padding-top: 10px !important;
    }

</style>
""", unsafe_allow_html=True)


# --- Encabezado principal ---
st.markdown(
    "<h1 class='main-title'>🤖 ChatBot IA - Universidad de Caldas</h1>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <p class='main-subtitle'>
        Aprende sobre <b>Inteligencia Artificial</b> con un asistente académico.  
        Pregunta sobre <i>conceptos, historia, aprendizaje automático, ética o regulaciones.</i>
    </p>
    """,
    unsafe_allow_html=True
)

# --- Historial session ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Input y modo ---
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("💬 Escribe tu pregunta:")
with col2:
    mode = st.selectbox("Modo", ["breve", "extendido"])

# --- Botón enviar ---
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
                        "latency": latency,
                        "mode": mode
                    })
                else:
                    st.error(f"❌ Error del servidor ({response.status_code})")
            except Exception as e:
                st.error(f"⚠️ Error al conectar con el backend: {e}")

# --- Mostrar historial ---
if st.session_state.history:
    st.markdown("## 💬 Historial de conversación")
    for item in reversed(st.session_state.history):
        st.markdown(f"**🧑‍🎓 Tú:** {item['question']}")
        st.markdown(f"**🤖 ChatBot:** {item['answer']}")
        st.caption(f"⏱️ {item['latency']} s | Modo: {item['mode']}")
        if item["citations"]:
            with st.expander("📚 Fuentes citadas"):
                for c in item["citations"]:
                    st.markdown(f"- {c}")
        st.markdown("---")

# --- Sidebar ---
st.sidebar.header("ℹ️ Información")
st.sidebar.info(
    """
    **Proyecto académico** desarrollado por:
    - Heidy 🧩  *(Líder contenido/UX - Contexto & UX)*
    - Julián 💡  *(Líder evaluación - LLM & Evaluación)*
    - Edwar ⚙️ *(Líder técnico - Infra & MLOps)*  

    ---
    💻 **Stack:** FastAPI + Streamlit + Docker  
    📊 Monitoreo: métricas, logs anonimizados  
    🔐 Seguridad: variables .env y control local
    """
)

st.sidebar.markdown("---")
st.sidebar.write("Universidad de Caldas © 2025")
