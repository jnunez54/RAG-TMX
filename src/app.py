import streamlit as st
import time

from database import DBHandler
from agents import MainAgent

st.set_page_config(page_title="RAG-TMX", layout="wide")

# Título de la app
st.title("🤖 [RAG-TMX]")
st.subheader("Chatbot para trámites mexicanos")
st.markdown("Powered by [Transformers] - [ChromaDB] - [Granite2B]")

# --- Inicialización de sesión ---
if "history" not in st.session_state:
    # Cada elemento: {"query": str, "response": str, "thought": str}
    st.session_state.history = []

# Placeholder donde volcamos toda la conversación
chat_placeholder = st.empty()

def display_conversation():
    """Renderiza todo el historial de la conversación, incluyendo el proceso de pensamiento."""
    md = ""
    for turn in st.session_state.history:
        md += f"**🧍 Tú:** {turn['query']}\n\n"
        md += f"**🤖 TMX:** {turn['response']}\n\n"
        if turn.get("thought"):
            md += (
                "<details>\n"
                "  <summary>🧠 <em>Proceso de pensamiento</em></summary>\n\n"
                f"  {turn['thought']}\n\n"
                "</details>\n\n"
            )
    chat_placeholder.markdown(md, unsafe_allow_html=True)

display_conversation()

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Escribe tu pregunta:", placeholder="¿En qué puedo ayudarte?")
    send = st.form_submit_button("Enviar")

if send and user_input:
    st.session_state.history.append({
        "query": user_input,
        "response": "",
        "thought": ""
    })
    display_conversation()  # refresh
    db_handler = DBHandler()
    agent = MainAgent(db_handler)

    for token in agent.chat(user_input):
        st.session_state.history[-1]["response"] += token
        display_conversation()

    # Al terminar, obtenemos el proceso de pensamiento
    try:
        thought_text = agent.get_thinking()
    except AttributeError:
        thought_text = ""
    st.session_state.history[-1]["thought"] = thought_text
    display_conversation()