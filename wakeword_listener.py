import os
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import numpy as np

class WakeWordListener:
    def __init__(self, wakeword="jarvis"):
        """Initialisiert die Wake-Word-Erkennung"""
        self.wakeword = wakeword
        self.handle = pvporcupine.create(
            access_key=self.load_access_key(),
            keywords=[wakeword]
        )

        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format=pyaudio.paInt16,  
            channels=1,  
            rate=16000, 
            input=True,
            frames_per_buffer=self.handle.frame_length
        )

    def listen_for_wakeword(self):
        """Hört auf das Wake-Word und gibt True zurück, wenn erkannt"""
        print("🎤 Warte auf Wake-Word...")
        while True:
            pcm = np.frombuffer(self.stream.read(self.handle.frame_length, exception_on_overflow=False), dtype=np.int16)
            keyword_index = self.handle.process(pcm)
            if keyword_index >= 0:
                print("🚀 Wake-Word erkannt!")
                return True  

    def cleanup(self):
        """Ressourcen aufräumen"""
        self.stream.close()
        self.pa.terminate()
        self.handle.delete()
        
    def load_access_key(self):
        """Lädt den Picovoice Access Key aus der Umgebungsvariable"""
        load_dotenv()
        return os.getenv("PICO_ACCESS_KEY")

