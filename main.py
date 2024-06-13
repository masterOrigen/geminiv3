import os
import streamlit as st
from PIL import Image
from PyPDF2 import PdfFileReader
from streamlit_option_menu import option_menu
from gemini_utility import (load_gemini_pro_model, gemini_pro_response,
                            gemini_pro_vision_response, embeddings_model_response)

working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="GPT MEDIOS - Gemini AI",
    layout="centered",
)

with st.sidebar:
    selected = option_menu('Gemini AI',
                           ['ChatBot',
                            'Resumen de Imagenes',
                            'Embeber texto',
                            'Preguntas y Respuestas'],
                           menu_icon='robot', icons=['chat-dots-fill', 'image-fill', 'textarea-t', 'patch-question-fill'],
                           default_index=0
                           )

# Función para traducir roles entre Gemini-Pro y Streamlit
def traducir_rol_para_streamlit(rol_usuario):
    if rol_usuario == "modelo":
        return "asistente"
    else:
        return rol_usuario

# Página del chatbot
if selected == 'ChatBot':
    modelo = load_gemini_pro_model()
    if "sesion_chat" not in st.session_state:
        st.session_state.sesion_chat = modelo.start_chat(historia=[])
    st.title("ChatBot GPT MEDIOS")
    for mensaje in st.session_state.sesion_chat.historia:
        with st.chat_message(traducir_rol_para_streamlit(mensaje.rol)):
            st.markdown(mensaje.partes[0].texto)
    pregunta_usuario = st.chat_input("Pregunta a Gemini-Pro...")
    if pregunta_usuario:
        st.chat_message("usuario").markdown(pregunta_usuario)
        respuesta_gemini = st.session_state.sesion_chat.send_message(pregunta_usuario)
        with st.chat_message("asistente"):
            st.markdown(respuesta_gemini.texto)

# Página de resumen de imágenes
if selected == "Resumen de Imagenes":
    st.title("📷 Imágenes")
    archivo_subido = st.file_uploader("Sube una imagen o archivo PDF:", type=["jpg", "jpeg", "png", "pdf"])
    if archivo_subido is not None:
        if archivo_subido.type.startswith('image'):
            imagen = Image.open(archivo_subido)
            col1, col2 = st.columns(2)
            with col1:
                imagen_redimensionada = imagen.resize((800, 500))
                st.image(imagen_redimensionada)
            prompt_predeterminado = "Escribe un resumen sobre lo que puedes ver en esta imagen, siempre tu respuesta debe ser en español."
            descripcion = gemini_pro_vision_response(prompt_predeterminado, imagen)
            with col2:
                st.info(descripcion)
        elif archivo_subido.type == 'application/pdf':
            st.write("Archivo PDF subido:", archivo_subido.name)
            # Leer el contenido del PDF
            with open(archivo_subido.name, "rb") as f:
                pdf_reader = PdfFileReader(f)
                text = ""
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    text += page.extractText()
            # Generar un resumen del contenido del PDF
            resumen = embeddings_model_response(text)
            st.header("Resumen del contenido del PDF:")
            st.write(resumen)

# Página del modelo de incrustación de texto
if selected == "Embeber texto":
    st.title("🔡 Incrustar Texto")
    prompt_usuario = st.text_area(label='', placeholder="Ingresa el texto para obtener incrustaciones")
    if st.button("Obtener Respuesta"):
        respuesta = embeddings_model_response(prompt_usuario)
        st.markdown(respuesta)

# Página del modelo de preguntas y respuestas
if selected == "Preguntas y Respuestas":
    st.title("Preguntas y Respuestas❓")
    pregunta_usuario = st.text_area(label='', placeholder="Escribe tu consulta...")
    if st.button("Obtener Respuesta"):
        respuesta = gemini_pro_response(pregunta_usuario)
        st.markdown(respuesta)
