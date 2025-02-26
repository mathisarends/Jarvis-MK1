import asyncio
from wakeword_listener import WakeWordListener
from whisper_speech_recognition import WhuisperSpeechRecognition
from chat_assistant import OpenAIChatAssistant

async def main():
    wakeword_listener = WakeWordListener(wakeword="jarvis")
    speech_recognizer = WhuisperSpeechRecognition()
    chat_assistant = OpenAIChatAssistant()

    try:
        while True:
            if wakeword_listener.listen_for_wakeword():
                wakeword_listener.pause_listening()
                
                try:
                    audio_file = speech_recognizer.record_audio()

                    text = speech_recognizer.transcribe_audio(audio_file)
                    print(text)
                    
                    if text:
                        print(f"🗣 Erkannt: {text}")
                        await chat_assistant.speak_response(text)
                        
                finally:
                    wakeword_listener.resume_listening()

    except KeyboardInterrupt:
        print("🛑 Manuelles Beenden.")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    finally:
        wakeword_listener.cleanup()

if __name__ == "__main__":
    asyncio.run(main())