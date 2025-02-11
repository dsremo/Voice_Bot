! pip install google-generativeai SpeechRecognition pyttsx3 pyaudio wave langdetect gtts pygame

import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import pyaudio
import wave
import tempfile
import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext, font
from langdetect import detect
from gtts import gTTS
import os
import tempfile
import pygame

WAKE_WORD = 'striker'
conversation_mode = False
max_retries = 5
retries = 0

r = sr.Recognizer()
mic_source = sr.Microphone()

GOOGLE_API_KEY = 'AIzaSyDKdR4PCzwCv52RoW4IXX-PwxRo7hrmkog'
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
convo = model.start_chat()

system_message = (
    "INSTRUCTIONS: You are a voice assistant. Respond to prompts with meaningful, coherent responses. "
    "Provide helpful and informative answers and avoid irrelevant responses. Prioritize logic and facts. "
    "Answer in the same language in which the question is asked."
)
convo.send_message(system_message.replace('\n', ' '))

def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Default to English if detection fails

def speak(text):
    lang = detect_language(text)
    print(f"Detected Language: {lang}")

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Check if a suitable voice is available
    selected_voice = None
    for voice in voices:
        if lang in voice.id or lang in voice.name.lower():
            selected_voice = voice.id
            break

    if selected_voice:
        # Use pyttsx3 if a voice is available
        engine.setProperty('voice', selected_voice)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        engine.say(text)
        engine.runAndWait()
    else:
        # Fallback to gTTS for unsupported languages
        print(f"No system voice found for {lang}. Using gTTS.")
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_filename = temp_audio.name
        tts.save(temp_filename)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()
        os.remove(temp_filename)

def transcribe_audio(audio_path):
    global retries
    try:
        with sr.AudioFile(audio_path) as source_audio:
            audio_data = r.record(source_audio)
            text = r.recognize_google(audio_data)
            retries = 0
            return text
    except sr.UnknownValueError:
        VoiceBotGUI.log_message("Could not understand the audio.", "error")
        retries += 1
        if retries >= max_retries:
            VoiceBotGUI.log_message("Max retries reached. Exiting.", "error")
            os._exit(1)
        return ""
    except sr.RequestError as e:
        VoiceBotGUI.log_message(f"Request failed: {e}", "error")
        retries += 1
        if retries >= max_retries:
            VoiceBotGUI.log_message("Max retries reached. Exiting.", "error")
            os._exit(1)
        return ""

def detect_wake_word(audio):
    global conversation_mode
    try:
        wake_audio_path = 'wake_detect.wav'
        with open(wake_audio_path, 'wb') as f:
            f.write(audio.get_wav_data())
        text_input = transcribe_audio(wake_audio_path)
        os.remove(wake_audio_path)
        VoiceBotGUI.log_message("Heard (wake detection): " + text_input, "info")
        if WAKE_WORD in text_input.lower():
            VoiceBotGUI.log_message("Wake word detected.", "info")
            speak("I'm listening. Please speak your prompt.")
            conversation_mode = True
    except Exception as e:
        VoiceBotGUI.log_message(f"Error detecting wake word: {e}", "error")

def prompt_gemini(audio):
    global conversation_mode
    try:
        prompt_audio_path = 'prompt.wav'
        with open(prompt_audio_path, 'wb') as f:
            f.write(audio.get_wav_data())
        prompt_text = transcribe_audio(prompt_audio_path)
        os.remove(prompt_audio_path)
        prompt_text = prompt_text.strip()
        VoiceBotGUI.log_message("User: " + prompt_text, "user")
        
        if prompt_text.lower() in ["exit", "end"]:
            speak("Exiting. Goodbye!")
            VoiceBotGUI.log_message("Exiting as per user command.", "info")
            VoiceBotGUI.root.quit()
            os._exit(0)

        if not prompt_text:
            speak("I didn't catch that. Please speak your prompt again.")
        else:
            convo.send_message(prompt_text)
            output = convo.last.text
            VoiceBotGUI.log_message("Striker: " + output, "bot")
            speak(output)
    except Exception as e:
        VoiceBotGUI.log_message(f"Error processing prompt: {e}", "error")

def callback(recognizer, audio):
    try:
        if not conversation_mode:
            detect_wake_word(audio)
        else:
            prompt_gemini(audio)
    except Exception as e:
        VoiceBotGUI.log_message(f"Error in callback: {e}", "error")

def start_listening():
    with mic_source as s:
        r.adjust_for_ambient_noise(s, duration=2)
    VoiceBotGUI.log_message(f"Say '{WAKE_WORD}' to start the conversation.", "info")
    r.listen_in_background(mic_source, callback)

class VoiceBotGUI:
    root = tk.Tk()
    
    @staticmethod
    def log_message(message, msg_type="normal"):
        colors = {
            "normal": "#ffffff",
            "info": "#00ff00",
            "error": "#ff5555",
            "user": "#00aaff",
            "bot": "#ffdd00",
        }
        def append():
            VoiceBotGUI.text_widget.configure(state="normal")
            VoiceBotGUI.text_widget.insert(tk.END, message + "\n", msg_type)
            VoiceBotGUI.text_widget.see(tk.END)
            VoiceBotGUI.text_widget.configure(state="disabled")
        VoiceBotGUI.root.after(0, append)
    
    def __init__(self):
        self.root.title("Striker VoiceBot")
        self.root.configure(bg="#2b2b2b")
        
        self.text_widget = scrolledtext.ScrolledText(self.root, wrap="word", state="disabled", height=20, width=60,
                                                     bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff")
        self.text_widget.pack(padx=10, pady=10)
        
        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_bot, bg="#ff5555", fg="#ffffff")
        self.exit_button.pack(pady=(0, 10))
        
        VoiceBotGUI.text_widget = self.text_widget
        VoiceBotGUI.root = self.root
    
    def exit_bot(self):
        speak("Exiting. Goodbye!")
        self.root.quit()
        os._exit(0)
    
    def run(self):
        self.root.mainloop()

def run_voicebot():
    start_listening()
    while True:
        time.sleep(0.5)

if __name__ == '__main__':
    gui = VoiceBotGUI()
    voicebot_thread = threading.Thread(target=run_voicebot, daemon=True)
    voicebot_thread.start()
    gui.run()
