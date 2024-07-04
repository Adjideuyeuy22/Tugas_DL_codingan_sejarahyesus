import requests
import os
from dotenv import load_dotenv
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

# Memuat variabel lingkungan dari file .env
load_dotenv()

API_KEY = os.getenv('GEMINI_API_KEY')

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
instruction = (  "Dalam percakapan ini, berikan jawaban tentang Yesus seolah-olah Anda menjelaskannya kepada anak berusia lima tahun."
)

# Inisialisasi pyttsx3 untuk sintesis suara
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Pilih suara bahasa Indonesia jika tersedia
selected_voice = None
for voice in voices:
    if 'indonesia' in voice.name.lower():  # Mencari suara bahasa Indonesia
        selected_voice = voice
        break

if selected_voice:
    engine.setProperty('voice', selected_voice.id)
else:
    print("Suara bahasa Indonesia tidak tersedia. Menggunakan suara default.")

engine.setProperty('rate', 180)  # Atur kecepatan suara yang lebih tinggi
engine.setProperty('volume', 1.0)

# Inisialisasi recognizer untuk pengenalan suara
recognizer = sr.Recognizer()

def text_to_speech(text):
    # Generate speech
    engine.save_to_file(text, 'ngomong.wav')
    engine.runAndWait()
    
    # Load generated speech with pydub
    sound = AudioSegment.from_file('ngomong.wav', format='wav')
    
    # Change pitch
    octaves = 0.5  # Change this to adjust pitch, <1.0 for lower pitch, >1.0 for higher pitch
    new_sample_rate = int(sound.frame_rate * (1.0 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate}).set_frame_rate(sound.frame_rate)
    
    # Play modified sound
    play(hipitch_sound)

def recognize_speech():
    with sr.Microphone() as source:
        print("Virtual Assistant: Mendengarkan...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            print("Virtual Assistant: Mengenali...")
            text = recognizer.recognize_google(audio, language='id-ID')
            print(f"Kamu: {text}")
            return text
        except sr.UnknownValueError:
            print("Virtual Assistant: Maaf, saya tidak mengerti.")
        except sr.RequestError:
            print("Virtual Assistant: Maaf, ada masalah dengan layanan pengenalan suara.")
        return None

while True:
    question = recognize_speech()
    if question is None:
        continue

    if  "yesus" in question.lower():
        response_text = chat.send_message(instruction + question).text
        response = response_text  # Menampilkan respons lengkap tanpa filter
    elif "yesus" not in question.lower():
        response = "Maaf, saya hanya memberikan informasi tentang Menggali sejarah yesus kristus."
    else:
        response = "Maaf, saya tidak memberikan penjelasan tentang ini."

    print('\n')
    print(f"Bot: {response}")
    print('\n')
    text_to_speech(response)
    instruction = ''
