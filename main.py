import asyncio
from wakeword_listener import WakeWordListener
from whisper_speech_recognition import WhuisperSpeechRecognition
from audio_transcriber import AudioTranscriber
from chat_assistant import OpenAIChatAssistant
from dotenv import load_dotenv

load_dotenv(override=True)

async def main():
    wakeword_listener = WakeWordListener(wakeword="jarvis")
    speech_recognizer = WhuisperSpeechRecognition()
    audio_transcriber = AudioTranscriber()
    chat_assistant = OpenAIChatAssistant()

    try:
        while True:
            if wakeword_listener.listen_for_wakeword():
                wakeword_listener.pause_listening()
                
                try:
                    audio_file = speech_recognizer.record_audio()
                    spoken_user_prompt = audio_transcriber.transcribe_audio(audio_file)

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