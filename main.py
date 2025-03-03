import asyncio
from wakeword_listener import WakeWordListener
from whisper_speech_recognition import WhuisperSpeechRecognition
from audio_transcriber import AudioTranscriber
from chat_assistant import OpenAIChatAssistant
from dotenv import load_dotenv
from audio.speech_to_text.speech_to_text_recorder import SpeechRecognition

load_dotenv(override=True)

async def main():
    wakeword_listener = WakeWordListener(wakeword="jarvis")
    speech_recognition = SpeechRecognition()
    chat_assistant = OpenAIChatAssistant()

    try:
        while True:
            if wakeword_listener.listen_for_wakeword():
                wakeword_listener.pause_listening()
                
                try:
                    spoken_user_prompt = speech_recognition.record_user_prompt()

                    if spoken_user_prompt is None:
                        continue
                    
                    print(f"🗣 Erkannt: {spoken_user_prompt}")
                    await chat_assistant.speak_response(spoken_user_prompt)
                        
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