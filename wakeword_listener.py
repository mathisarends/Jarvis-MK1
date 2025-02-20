import os
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import numpy as np
from sound_player import SoundPlayer
import threading
import time

class WakeWordListener:
    """Erkennt das Wake-Word und gibt ein Signal aus."""

    def __init__(self, wakeword="jarvis"):
        """Initialisiert die Wake-Word-Erkennung."""
        self.wakeword = wakeword
        self.handle = pvporcupine.create(
            access_key=self.load_access_key(),
            keywords=[wakeword]
        )

        # Separate PyAudio-Instanz für Input
        self.pa_input = pyaudio.PyAudio()
        self.stream = self.pa_input.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=self.handle.frame_length,
            stream_callback=self._audio_callback
        )
        
        # Flags für Status
        self.is_listening = False
        self.should_stop = False
        self._detection_event = threading.Event()
        
        # Separate Instanz für Sound-Player
        self.sound_player = SoundPlayer()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback für Audio-Processing"""
        if self.is_listening and not self.should_stop:
            pcm = np.frombuffer(in_data, dtype=np.int16)
            keyword_index = self.handle.process(pcm)
            
            if keyword_index >= 0:
                print("🚀 Wake-Word erkannt!")
                self._detection_event.set()
                self.sound_player.play_listening_sound()
        
        return (in_data, pyaudio.paContinue)

    def listen_for_wakeword(self):
        """Hört auf das Wake-Word und gibt True zurück, wenn erkannt."""
        print("🎤 Warte auf Wake-Word...")
        self.is_listening = True
        self.stream.start_stream()
        
        # Warten auf Erkennung mit Timeout
        while not self.should_stop:
            if self._detection_event.wait(timeout=0.1):  # 100ms Timeout
                self._detection_event.clear()
                return True
        
        return False

    def cleanup(self):
        """Ressourcen aufräumen."""
        print("🧹 Räume Wake-Word-Listener auf...")
        self.should_stop = True
        self.is_listening = False
        
        # Warte kurz, damit laufende Operationen beendet werden können
        time.sleep(0.2)
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa_input:
            self.pa_input.terminate()
        if self.handle:
            self.handle.delete()
        
        print("✅ Wake-Word-Listener erfolgreich beendet")
        
    def load_access_key(self):
        """Lädt den Picovoice Access Key aus der Umgebungsvariable."""
        load_dotenv()
        return os.getenv("PICO_ACCESS_KEY")

    def pause_listening(self):
        """Pausiert die Wake-Word-Erkennung temporär"""
        self.is_listening = False
        
    def resume_listening(self):
        """Setzt die Wake-Word-Erkennung fort"""
        self.is_listening = True