from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import random
import uuid
from gtts import gTTS
from google.cloud import language_v1

app = Flask(__name__)

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\saddi\Downloads\project1-436215-239f8d86051f.json"

# Create directories if they don't exist
TRANSCRIPTIONS_DIR = 'transcriptions'
AUDIO_FILES_DIR = 'audio_files'
os.makedirs(TRANSCRIPTIONS_DIR, exist_ok=True)
os.makedirs(AUDIO_FILES_DIR, exist_ok=True)

# Feedback phrases
feedback_phrases = [
    "Your words resonate clearly in the digital realm.",
    "Your voice paints a vivid picture in the canvas of sound.",
    "Each word you speak is a building block of communication.",
    "Your thoughts flow smoothly through the medium of speech.",
    "Your voice carries the power of your ideas.",
    "Clear communication is the bridge between confusion and clarity.",
    "Your words have the potential to inspire and inform.",
    "Speaking is the voice of the mind, listening is the nourishment of the heart.",
    "Your voice is a unique instrument in the orchestra of human expression.",
    "Every word you speak is a step towards better understanding."
]

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_speech():
    data = request.json
    transcription = data['transcription']
    
    # Perform sentiment analysis
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=transcription, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
    
    # Determine sentiment label
    sentiment_label = "Neutral"
    if sentiment.score > 0.25:
        sentiment_label = "Positive"
    elif sentiment.score < -0.25:
        sentiment_label = "Negative"
    
    # Save transcription to file
    filename = f"transcription_{uuid.uuid4()}.txt"
    file_path = os.path.join(TRANSCRIPTIONS_DIR, filename)
    with open(file_path, 'w') as f:
        f.write(f"Transcription: {transcription}\nSentiment: {sentiment_label}")
    
    feedback = random.choice(feedback_phrases)
    return jsonify({
        'transcription': transcription,
        'sentiment': sentiment_label,
        'file_path': f'/transcriptions/{filename}',
        'feedback': feedback
    })

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data['text']
    
    # Perform sentiment analysis
    client = language_v1.LanguageServiceClient()
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment
    
    # Determine sentiment label
    sentiment_label = "Neutral"
    if sentiment.score > 0.25:
        sentiment_label = "Positive"
    elif sentiment.score < -0.25:
        sentiment_label = "Negative"
    
    # Save text to file
    text_filename = f"text_{uuid.uuid4()}.txt"
    text_path = os.path.join(TRANSCRIPTIONS_DIR, text_filename)
    with open(text_path, 'w') as f:
        f.write(f"Text: {text}\nSentiment: {sentiment_label}")
    
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    audio_filename = f"audio_{uuid.uuid4()}.mp3"
    audio_path = os.path.join(AUDIO_FILES_DIR, audio_filename)
    tts.save(audio_path)
    
    return jsonify({
        'text_path': f'/transcriptions/{text_filename}',
        'audio_path': f'/audio_files/{audio_filename}',
        'sentiment': sentiment_label
    })

@app.route('/transcriptions/<path:filename>')
def serve_transcription(filename):
    return send_from_directory(TRANSCRIPTIONS_DIR, filename)

@app.route('/audio_files/<path:filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FILES_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)