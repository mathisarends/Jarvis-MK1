import threading
import pygame
import os
from pydub import AudioSegment
from io import BytesIO

# Umstellen auf 

class SoundPlayer:
    """Verwaltet das Abspielen des Wake-Word-Sounds in einem separaten Thread."""
    
    def __init__(self, file_path):
        self.base_path = os.path.dirname(__file__)
        self._setup_pygame()
        self._audio_lock = threading.Lock()
        
        full_path = os.path.join(self.base_path, file_path)
        self.sound = AudioSegment.from_file(full_path)

    def _setup_pygame(self):
        pygame.mixer.init()

    def _play_audio_thread(self):
        with self._audio_lock:
            try:
                audio_io = BytesIO()
                self.sound.export(audio_io, format="wav")
                audio_io.seek(0)

                pygame.mixer.music.load(audio_io)
                pygame.mixer.music.play()

                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)

            except Exception as e:
                print(f"❌ Playback error: {e}")
            finally:
                pygame.mixer.music.stop()
                audio_io.close()

    def play_audio(self):
        threading.Thread(
            target=self._play_audio_thread,
            daemon=True
        ).start()