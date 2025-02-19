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
            
            if text:
                print(f"🗣 Erkannt: {text}")

                # ✅ GPT antwortet und spricht
                chat_assistant.speak_response(text)

            # ✅ Zurück in den Wake-Word-Modus
            print("🎤 Zurück zur Wake-Word-Erkennung...")
        
except KeyboardInterrupt:
    print("🛑 Manuelles Beenden.")

finally:
    wakeword_listener.cleanup()
