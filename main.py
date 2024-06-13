import os
from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
from gemini_utility import (load_gemini_pro_model,
                            gemini_pro_response,
                            gemini_pro_vision_response,
                            embeddings_model_response)
import PyPDF4
import io

# Establecer el directorio de trabajo
working_dir = os.path.dirname(os.path.abspath(__file__))

# Configurar la página de Streamlit
st.set_page_config(
    page_title="GTP MEDIOS - Gemini AI",
    layout="centered",
)

# Crear el menú de opciones en la barra lateral
with st.sidebar:
    selected = option_menu('GPT MEDIOS - Gemini AI',
                           ['ChatBot',
                            'Imagen',
                            'Texto Embebido',
                            'Pregunta Algo',
                            'Interacción PDF'],  # Nueva opción para interactuar con PDF
                           menu_icon='robot', icons=['chat-dots-fill', 'image-fill', 'textarea-t', 'patch-question-fill', 'file-pdf-fill'],  # Nuevo icono para PDF
                           default_index=0
                           )

# Función para traducir roles entre Gemini-Pro y Streamlit
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role

# Página del chatbot
if selected == 'ChatBot':
    model = load_gemini_pro_model()

    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    st.title("ChatBot IA")

    for message in st.session_state.chat_session.history:
        with st.chat_message(translate_role_for_streamlit(message.role)):
            st.markdown(message.parts[0].text)

    user_prompt = st.chat_input("Realizar consulta...")
    if user_prompt:
        st.chat_message("user").markdown(user_prompt)

        gemini_response = st.session_state.chat_session.send_message(user_prompt)

        with st.chat_message("assistant"):
            st.markdown(gemini_response.text)

# Página de generación de caption de imagen
if selected == "Imagen":
    st.title("Generar Caption")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if st.button("Generación de Caption"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 500))
            st.image(resized_img)

        default_prompt = "Escribre una descripción para esta imagen, recuerda responder siempre en español"

        caption = gemini_pro_vision_response(default_prompt, image)

        with col2:
            st.info(caption)

# Modelo de incrustación de texto
if selected == "Texto Embebido":
    st.title("🔡 Embeber Texto")

    user_prompt = st.text_area(label='', placeholder="Enter the text to get embeddings")

    if st.button("Respuesta"):
        response = embeddings_model_response(user_prompt)
        st.markdown(response)

# Preguntar cualquier cosa
if selected == "Pregunta Algo":
    st.title("Preguntar Algo")

    user_prompt = st.text_area(label='', placeholder="Pregunta Algo...")

    if st.button("Get Response"):
        response = gemini_pro_response(user_prompt)
        st.markdown(response)

# Interacción con PDF
if selected == "Interacción PDF":
    st.title("📄 PDF Interaction")

    uploaded_pdf = st.file_uploader("Subir PDF...", type="pdf")

    if uploaded_pdf is not None:
        st.write("PDF file uploaded:", uploaded_pdf.name)

        # Leer el contenido del PDF
        pdf_contents = uploaded_pdf.read()
        pdf_file = io.BytesIO(pdf_contents)
        reader = PyPDF4.PdfFileReader(pdf_file)
        text = ""
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()

        # Realizar preguntas sobre el contenido del PDF
        st.title("Ask questions about the PDF:")
        user_prompt_pdf = st.text_area(label='', placeholder="Preguntar sobre el PDF...")
        if st.button("Get Response"):
            response_pdf = gemini_pro_response(user_prompt_pdf, context=text)  # Aquí se pasa el contexto
            st.markdown(response_pdf)
