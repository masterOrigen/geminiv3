from PIL import Image
import streamlit as st
from streamlit_option_menu import option_menu
from gemini_utility import (load_gemini_pro_model,
                            gemini_pro_response,
                            gemini_pro_vision_response,
                            embeddings_model_response)
import PyPDF4
import io

working_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Gemini AI",
    page_icon="🧠",
    layout="centered",
)

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


# Function to translate roles between Gemini-Pro and Streamlit terminology
def translate_role_for_streamlit(user_role):
    if user_role == "model":
        return "assistant"
    else:
        return user_role


# chatbot page
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


# Image captioning page
if selected == "Imagen":
    st.title("Generar Caption")

    uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

    if st.button("Generación de Caption"):
        image = Image.open(uploaded_image)

        col1, col2 = st.columns(2)

        with col1:
            resized_img = image.resize((800, 500))
            st.image(resized_img)

        default_prompt = "write a short caption for this image"

        caption = gemini_pro_vision_response(default_prompt, image)

        with col2:
            st.info(caption)


# Text embedding model
if selected == "Embed text":
    st.title("🔡 Embed Text")

    user_prompt = st.text_area(label='', placeholder="Enter the text to get embeddings")

    if st.button("Get Response"):
        response = embeddings_model_response(user_prompt)
        st.markdown(response)


# Text embedding model
if selected == "Ask me anything":
    st.title("❓ Ask me a question")

    user_prompt = st.text_area(label='', placeholder="Ask me anything...")

    if st.button("Get Response"):
        response = gemini_pro_response(user_prompt)
        st.markdown(response)


# PDF Interaction page
if selected == "PDF Interaction":
    st.title("📄 PDF Interaction")

    uploaded_pdf = st.file_uploader("Upload a PDF file...", type="pdf")

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
        user_prompt_pdf = st.text_area(label='', placeholder="Ask a question about the PDF...")
        if st.button("Get Response"):
            response_pdf = gemini_pro_response(user_prompt_pdf, context=text)  # Aquí se pasa el contexto
            st.markdown(response_pdf)
