import os
from dotenv import load_dotenv
import pvporcupine
import struct
import pyaudio
import numpy as np
from scipy.signal import butter, lfilter

# ✅ Lade API-Key aus .env-Datei
load_dotenv()
ACCESS_KEY = os.getenv("PICO_ACCESS_KEY")
if not ACCESS_KEY:
    raise ValueError("❌ Kein Picovoice Access Key gefunden!")

# ✅ Wake-Word-Modell Pfad (Passe den Pfad an!)
wakeword_path = os.path.join(os.path.dirname(__file__), "../pico_wakewords/Jarvis_en_windows_v3_0_0.ppn")

# ✅ Initialisiere Porcupine mit niedriger Sensitivität
porcupine = pvporcupine.create(
    access_key=ACCESS_KEY, 
    keywords=["jarvis"], 
    sensitivities=[0.05]  # Weniger empfindlich (verringert False Positives)
)

# ✅ Initialisiere das Mikrofon mit Mono + 16 kHz
pa = pyaudio.PyAudio()
stream = pa.open(
    format=pyaudio.paInt16,
    channels=1,  # Erzwinge Mono
    rate=16000,  # Standard für Porcupine
    input=True,
    frames_per_buffer=porcupine.frame_length // 2  # Kleinere Blöcke testen
)

# 🎚 Noise-Gate Grenzwert für leise Geräusche
NOISE_THRESHOLD = 1500  

# 🎚 Low-Pass-Filter für weniger Rauschen
def butter_lowpass_filter(data, cutoff=1000, fs=16000, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, data)

print("🎤 Warte auf Wake-Word...")

while True:
    # ✅ Verwende NumPy für saubere PCM-Daten
    pcm = np.frombuffer(stream.read(porcupine.frame_length, exception_on_overflow=False), dtype=np.int16)

    # ✅ Falls das Signal zu leise ist, überspringe es
    if max(pcm) < NOISE_THRESHOLD:
        continue

    # ✅ Filtere das Audio, um Rauschen zu minimieren
    pcm = butter_lowpass_filter(pcm).astype(np.int16)

    # ✅ Wake-Word erkennen
    if porcupine.process(pcm):
        print("🚀 Wake-Word erkannt!")
        break  # Hier kannst du Whisper starten

# ✅ Ressourcen aufräumen
stream.close()
pa.terminate()
porcupine.delete()
