import time
from whisper_speech_recognition import WhuisperSpeechRecognition
import sounddevice as sd
import wave
import numpy as np

# Instanz der Klasse erstellen
speech_recognition = WhuisperSpeechRecognition()

# Datei für die Aufnahme
recorded_file = "./temp/recorded_audio.wav"

# Aufnahme starten
print("🎙 Sage etwas...")
recorded_file = speech_recognition.record_audio(recorded_file)

time.sleep(5)

if recorded_file:
    print(f"✅ Aufnahme gespeichert: {recorded_file}")
    
    # Wiedergabe der Aufnahme
    print("🔊 Spiele die Aufnahme ab...")

    def play_audio(filename):
        """Spielt eine WAV-Datei ab"""
        with wave.open(filename, "rb") as wf:
            samplerate = wf.getframerate()
            data = wf.readframes(wf.getnframes())
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Sound abspielen
            sd.play(audio_array, samplerate)
            sd.wait()  

    play_audio(recorded_file)
else:
    print("❌ Keine Aufnahme erkannt.")
