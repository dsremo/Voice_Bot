# Striker VoiceBot

Striker VoiceBot is a voice-controlled AI assistant that responds to spoken prompts using Google's Generative AI. It listens for a wake word ("striker") and engages in conversation using text-to-speech and speech recognition and answers in the same language in which the question is asked.

### -- Jupyter file can be run independently
### -- main.py can be run independently

## Features
- Voice-activated assistant using the wake word "striker"
- Speech recognition via Google Speech Recognition API
- Responses generated by Google Generative AI (Gemini API)
- Text-to-speech output using \`pyttsx3\`
- GUI log window for interactions
- Continuous background listening

## Installation
Ensure you have Python installed, then run:

\`\`\`sh
pip install google-generativeai SpeechRecognition pyttsx3 pyaudio wave
\`\`\`

### Additional Dependencies
- **Windows**: If \`pyaudio\` installation fails, install it manually:
  \`\`\`sh
  pip install path_to_pyaudio.whl
  \`\`\`
- **Linux (Ubuntu/Debian)**:
  \`\`\`sh
  sudo apt-get install portaudio19-dev
  pip install pyaudio
  \`\`\`

## Usage
Run the script:
\`\`\`sh
python striker_voicebot.py
\`\`\`
The assistant will start listening. Say **"striker"** to wake it up and give your prompt.

## Configuration
The script uses Google Generative AI, which requires an API key. Set your API key in the script:
\`\`\`python
GOOGLE_API_KEY = 'your_api_key_here'
genai.configure(api_key=GOOGLE_API_KEY)
\`\`\`

## Exit Commands
To exit, say **"exit"** or **"end"**, or click the **Exit** button in the GUI.

## Components
- **Speech Recognition**: Listens and transcribes voice input
- **Text-to-Speech (TTS)**: Converts AI-generated responses into speech
- **Generative AI (Gemini API)**: Generates responses to user queries
- **GUI (Tkinter)**: Displays conversation logs and status messages

## Notes
- Make sure your microphone is working properly.
- Background noise can affect recognition accuracy.
- The assistant prioritizes factual and coherent responses.

## License
MIT License

## Author
[Ashutosh Tiwari]
