import os
import tempfile
import base64
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import pyttsx3

# ----- Global Settings and Initialization -----
WAKE_WORD = 'striker'
conversation_mode = False

# Configure Google Generative AI (Gemini) API
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
)
convo.send_message(system_message.replace('\n', ' '))

# ----- Flask App Setup -----
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def speak(text):
    """
    Uses pyttsx3 to convert text to speech and saves the output to a temporary WAV file.
    Returns the filename.
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1)
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
    
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
            temp_filename = fp.name
        engine.save_to_file(text, temp_filename)
        engine.runAndWait()
        return temp_filename
    except Exception as e:
        print("Error in TTS:", e)
        raise


@app.route('/chat_text', methods=['POST'])
def chat_text():
    """
    Expects a JSON payload with a 'message' field.
    Processes the text according to conversation mode:
      - If conversation not started, waits for wake word.
      - If wake word is detected or conversation is active, processes user prompt.
      - If "exit" or "end" is received, ends conversation.
    Returns a JSON response containing:
      - "response_text": the bot's response text.
      - "audio_data": base64-encoded WAV file data.
    """
    global conversation_mode
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided."}), 400

        message = data['message'].strip()
        print("Received message:", message)

        # If conversation is not active, look for wake word or "wake" command.
        if not conversation_mode:
            if message.lower() == "wake" or message.lower().find(WAKE_WORD) != -1:
                conversation_mode = True
                response_text = "I'm listening. Please speak your prompt."
            else:
                response_text = "Please speak the wake‑up word “striker”."
        else:
            # Conversation mode active.
            if message.lower() in ["exit", "end"]:
                response_text = "Exiting. Goodbye!"
                conversation_mode = False
            elif message == "":
                response_text = "I didn't catch that. Please speak your prompt again."
            else:
                # Send the user's prompt to the Gemini model.
                convo.send_message(message)
                response_text = convo.last.text

        print("Response Text:", response_text)
        # Generate TTS audio from the response.
        tts_filename = speak(response_text)
        # Read the generated audio file and base64 encode it.
        with open(tts_filename, "rb") as f:
            audio_bytes = f.read()
        os.remove(tts_filename)
        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
        return jsonify({"response_text": response_text, "audio_data": encoded_audio})
    except Exception as e:
        print("Error in /chat_text:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

