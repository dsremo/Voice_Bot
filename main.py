from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import pyaudio
import os
import time

# Flask setup
app = Flask(__name__)

# Initialize speech recognizer
r = sr.Recognizer()
source = sr.Microphone()

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set up Gemini API
GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
convo = model.start_chat()

# Modify the system message
system_message = '''INSTRUCTIONS: You are a voice assistant. Respond to prompts with meaningful, coherent responses based on the input. 
Provide helpful and informative answers and avoid irrelevant responses. Prioritize logic and facts in your replies. 
You should not limit your responses to "AFFIRMATIVE" only.'''
system_message = system_message.replace(f'\n', '')
convo.send_message(system_message)

# Flask route for the homepage
@app.route('/')
def index():
    return render_template('index.html')  # Render a simple HTML page

# Flask route to handle audio input from the client
@app.route('/process_audio', methods=['POST'])
def process_audio():
    audio_file = request.files['audio']
    
    # Save the received audio file to disk
    audio_path = 'input_audio.wav'
    audio_file.save(audio_path)
    
    # Transcribe the audio and get the response from Gemini
    prompt_text = transcribe_audio(audio_path)
    
    if prompt_text:
        convo.send_message(prompt_text)
        output = convo.last.text
        return jsonify({'response': output})
    else:
        return jsonify({'response': 'Sorry, I couldn\'t understand that. Please try again.'})

def transcribe_audio(audio_path):
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return None

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.setProperty('voice', engine.getProperty('voices')[1].id)

    engine.save_to_file(text, 'output_audio.mp3')
    engine.runAndWait()

if __name__ == '__main__':
    app.run(debug=True)
