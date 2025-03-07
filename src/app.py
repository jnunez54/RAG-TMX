import streamlit as st
import time
import base64
import os

def parse_pdf(pdf_path):
    start_time = time.time()
    markdown_content = f"Contenido parseado de {pdf_path}, aqui se supone que va un monton de contenido parseado pero todvia no lo implemento, tecnologia es un termino general que se aplica al proceso por el cual los sers humanos dise;an herramientas para incrementar su control y suc omprension del entorno material que lo rodea"  
    time.sleep(2)
    elapsed_time = time.time() - start_time
    return markdown_content, elapsed_time

if 'pdf_index' not in st.session_state:
    st.session_state.pdf_index = 0

st.title("Test PDF Parser")

tipo_proceso = st.radio("Tipo de documento:", ["DOF(Digitalizado)", "Solicitudes de Transparencia"], horizontal=True)

if tipo_proceso == "DOF(Digitalizado)":
    path = "DOF"
    pdf_files = os.listdir("DOF")
else:
    path = "Solicitudes"
    pdf_files = os.listdir("Solicitudes")
    
col1, col2 = st.columns(2)
with col1:
    if st.button("← Anterior"):
        st.session_state.pdf_index = max(0, st.session_state.pdf_index - 1)
with col2:
    if st.button("Siguiente →"):
        st.session_state.pdf_index = min(len(pdf_files) - 1, st.session_state.pdf_index + 1)

current_pdf = pdf_files[st.session_state.pdf_index]

col1, col2 = st.columns(2)
with col1:
    with open(os.path.join(path, current_pdf), "rb") as pdf_file: 
        pdf_bytes = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="300" height="400" type="application/pdf"></iframe>'        
        st.markdown(pdf_display, unsafe_allow_html=True)
with col2:
    if st.button("Parsear PDF"):
        parsed_content, parse_time = parse_pdf(current_pdf)
        st.session_state.parsed_content = parsed_content
        st.session_state.parse_time = parse_time
    
    if 'parsed_content' in st.session_state:
        st.markdown(f"**Tiempo de parseo:** {st.session_state.parse_time:.2f} segundos")
        st.markdown("---")
        st.markdown(st.session_state.parsed_content, unsafe_allow_html=True)
