import os
import requests
import pyttsx3
from flask import Flask, render_template, request, send_from_directory
from moviepy.editor import *

app = Flask(__name__)

# Função para buscar imagem no Unsplash
def get_unsplash_image(query, access_key):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}&count=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        image_data = response.json()
        image_url = image_data[0]['urls']['regular']
        img_data = requests.get(image_url).content
        image_filename = 'static/generated_image.jpg'
        with open(image_filename, 'wb') as handler:
            handler.write(img_data)
        return image_filename
    else:
        return None

# Função para gerar áudio a partir de texto
def generate_audio_from_text(text):
    engine = pyttsx3.init()
    audio_filename = 'static/output_audio.mp3'
    engine.save_to_file(text, audio_filename)
    engine.runAndWait()
    return audio_filename

# Função para criar o vídeo
def create_video(image_file, audio_file):
    image_clip = ImageClip(image_file)
    audio_clip = AudioFileClip(audio_file)
    image_clip = image_clip.with_duration(audio_clip.duration)
    video_clip = image_clip.with_audio(audio_clip)
    video_filename = 'static/final_video.mp4'
    video_clip.write_videofile(video_filename, fps=24)
    return video_filename

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        text_input = request.form["text_input"]
        unsplash_access_key = '8izMGO31TwbCL3h3nlHXQfxbEFWY_K723Q-frL-uKf4'  # Substitua com sua chave de API do Unsplash

        # Passo 1: Buscar imagem do Unsplash
        image_file = get_unsplash_image(text_input, unsplash_access_key)
        if not image_file:
            return "Erro ao buscar imagem."

        # Passo 2: Gerar áudio a partir de texto
        audio_file = generate_audio_from_text(text_input)

        # Passo 3: Criar vídeo
        video_file = create_video(image_file, audio_file)

        # Retornar o vídeo gerado para o usuário
        return render_template("index.html", video_url=video_file)

    return render_template("index.html", video_url=None)

# Rota para baixar o vídeo
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    app.run(debug=True)
