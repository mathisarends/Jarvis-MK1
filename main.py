from wakeword_listener import WakeWordListener
from whisper_speech_recognition import WhuisperSpeechRecognition

# ✅ Initialisiere Wake-Word-Listener & Whisper API-Nutzung
wakeword_listener = WakeWordListener(wakeword="jarvis")
speech_recognizer = WhuisperSpeechRecognition()

try:
    while True:
        if wakeword_listener.listen_for_wakeword():
            # ✅ Aufnahme starten & als MP3 speichern
            audio_file = speech_recognizer.record_audio(filename="speech.mp3")

            # ✅ Transkription mit OpenAI Whisper API
            text = speech_recognizer.transcribe_audio(audio_file)
            
            print(f"🗣 Erkannt: {text}")

            # ✅ Zurück in den Wake-Word-Modus
            print("🎤 Zurück zur Wake-Word-Erkennung...")
        
except KeyboardInterrupt:
    print("🛑 Manuelles Beenden.")

finally:
    wakeword_listener.cleanup()
