import json
import queue
import os
from dotenv import load_dotenv

import openai
import sounddevice as sd
from vosk import Model, KaldiRecognizer

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ Kein OpenAI API-Key gefunden! Bitte in .env speichern.")

openai.api_key = OPENAI_API_KEY

# 🎤 Vosk Modell für Wake-Word-Erkennung
MODEL_PATH = "../vosk-model-small-de-0.15"
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"❌ Vosk-Modell nicht gefunden: {MODEL_PATH}")

model = Model(MODEL_PATH)
recognizer = KaldiRecognizer(model, 16000)

audio_queue = queue.Queue()

WAKE_WORD = "jarvis"

# 🔊 Callback-Funktion für die Mikrofonaufnahme
def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Sounddevice-Fehler: {status}", flush=True)
    audio_queue.put(bytes(indata))

# 📢 Whisper-Transkription über OpenAI API
def transcribe_with_whisper(audio_bytes):
    print("⏳ Sende Audio an Whisper...")
    
    response = openai.Audio.transcriptions.create("whisper-1", audio_bytes, filetype="wav")
    text = response.get("text", "").strip()

    if text:
        print(f"🎤 Whisper-Transkription: {text}")
    else:
        print("⚠️ Keine Sprache erkannt.")

# 🎙️ Mikrofonaufnahme starten
with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                       channels=1, callback=callback):
    print("🎤 Sprich jetzt ... Sage das Wake-Word zum Aktivieren.")

    recording = False
    audio_data = []

    while True:
        data = audio_queue.get()
        
        # 🎯 Falls kein Signal erkannt wird → Nichts tun
        if not recognizer.AcceptWaveform(data):
            continue
        
        # 📝 Erkannten Text aus Vosk abrufen
        result = json.loads(recognizer.Result())
        text = result.get("text", "").lower()

        print(f"🔎 Erkannt: {text}")

        # 🎯 Wake-Word erkannt → Aufnahme starten
        if WAKE_WORD in text:
            print("🚀 Wake-Word erkannt! Aufnahme gestartet...")
            recording = True
            audio_data.clear()
            continue

        # 🎯 Falls aktuell keine Aufnahme läuft → Überspringen
        if not recording:
            continue

        # 🎙️ Während der Aufnahme → Audio speichern
        audio_data.append(data)

        # 🎯 Aufnahme beenden, wenn "stop" erkannt wird oder genug Audio gesammelt wurde
        if "stop" in text or len(audio_data) > 50:
            print("⏹️ Aufnahme beendet. Senden an Whisper...")
            recording = False

            # 📢 Whisper API aufrufen (direkt aus dem Speicher, kein Speichern notwendig)
            transcribe_with_whisper(b"".join(audio_data))
