import os
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import numpy as np

load_dotenv()
ACCESS_KEY = os.getenv("PICO_ACCESS_KEY")
if not ACCESS_KEY:
    raise ValueError("❌ Kein Picovoice Access Key gefunden!")

# Initialisiere Porcupine
handle = pvporcupine.create(
    access_key=ACCESS_KEY,
    keywords=["jarvis"]
)

# Initialisiere das Mikrofon 
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,  
    channels=1,  
    rate=16000,  
    input=True,
    frames_per_buffer=handle.frame_length
)

print("🎤 Warte auf Wake-Word...")

try:
    while True:
        # ✅ Lies ein Frame vom Mikrofon
        pcm = np.frombuffer(stream.read(handle.frame_length, exception_on_overflow=False), dtype=np.int16)

        # ✅ Wake-Word erkennen
        keyword_index = handle.process(pcm)
        if keyword_index >= 0:
            print("🚀 Wake-Word erkannt!")
            break

except KeyboardInterrupt:
    print("🛑 Beende das Programm.")

finally:
    # ✅ Ressourcen aufräumen
    stream.close()
    pa.terminate()
    handle.delete()
