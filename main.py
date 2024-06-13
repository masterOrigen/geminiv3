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
import requests

# Establecer el directorio de trabajo
working_dir = os.path.dirname(os.path.abspath(__file__))

# Configurar la página de Streamlit
st.set_page_config(
    page_title="GTP MEDIOS - Gemini AI",
    layout="centered",
)

# Crear el menú de opciones en la barra lateral
with st.sidebar:
    selected = st.selectbox('GPT MEDIOS - Gemini AI',
                           ['ChatBot',
                            'Imagen',
                            'Texto Embebido',
                            'Pregunta Algo',
                            'Interacción PDF',
                            'Video YouTube'],  # Nueva opción para interactuar con videos de YouTube
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
        st.title("Preguntar sobre el PDF:")
        user_prompt_pdf = st.text_area(label='', placeholder="Realizar Consulta...")
        if st.button("Get Response"):
            response_pdf = gemini_pro_response(user_prompt_pdf, context=text)  # Aquí se pasa el contexto
            st.markdown(response_pdf)

# Página de interacción con videos de YouTube
if selected == "Video YouTube":
    st.title("📺 Video YouTube")

    youtube_url = st.text_input("Inserta la URL del video de YouTube")

    if youtube_url:
        video_id = youtube_url.split("=")[-1]

        # Llamar a la API de YouTube para obtener información sobre el video
        api_key = "AIzaSyBVUkC1ka0lOWD3qk6ldQjqjgDlzCqNT5M"
        base_url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "id": video_id,
            "key": api_key
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code == 200 and data.get("items"):
            video_info = data["items"][0]["snippet"]
            st.write(f"Título: {video_info['title']}")
            st.write(f"Descripción: {video_info['description']}")
            st.write(f"Fecha de publicación: {video_info['publishedAt']}")
            st.write(f"Canal: {video_info['channelTitle']}")

            st.header("Realizar una pregunta sobre el video:")
            pregunta = st.text_area("Escribe tu pregunta aquí:")
            if st.button("Enviar pregunta"):
                # Llamar a la función gemini_pro_response para obtener una respuesta a la pregunta
                respuesta = gemini_pro_response(pregunta)
                st.write("Respuesta:", respuesta)

        else:
            st.error("No se pudo obtener la información del video. Por favor, verifica la URL y asegúrate de que el video sea público.")
