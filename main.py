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
