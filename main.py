from wakeword_listener import WakeWordListener
from whisper_speech_recognition import WhuisperSpeechRecognition
from chat_assistant import OpenAIChatAssistant

# ✅ Initialisiere Wake-Word-Listener & Whisper API-Nutzung
wakeword_listener = WakeWordListener(wakeword="jarvis")
speech_recognizer = WhuisperSpeechRecognition()
chat_assistant = OpenAIChatAssistant()

try:
    while True:
        if wakeword_listener.listen_for_wakeword():
            # ✅ Aufnahme starten & als MP3 speichern
            audio_file = speech_recognizer.record_audio()

            # ✅ Transkription mit OpenAI Whisper API
            text = speech_recognizer.transcribe_audio(audio_file)
            print(text)
            
            if text is None:
                continue
            
            print(f"🗣 Erkannt: {text}")

            chat_assistant.speak_response(text)

except KeyboardInterrupt:
    print("🛑 Manuelles Beenden.")

except Exception as e:
    print(f"❌ Fehler: {e}")

finally:
    wakeword_listener.cleanup()
