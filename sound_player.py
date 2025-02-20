import threading
import pygame
from pydub import AudioSegment
from io import BytesIO

class SoundPlayer:
    """Verwaltet das Abspielen des Wake-Word-Sounds in einem separaten Thread."""
    
    def __init__(self, sound_file="./audio/listening.mp3"):
        """Initialisiert die Sound-Wiedergabe."""
        self.sound = AudioSegment.from_file(sound_file)
        self._setup_pygame()
        self._audio_lock = threading.Lock()

    def _setup_pygame(self):
        """Initialisiert pygame für die Audio-Wiedergabe."""
        pygame.mixer.init()

    def _play_audio_thread(self):
        """Spielt das Audio im Hintergrund ab, synchronisiert mit Lock."""
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

    def play_listening_sound(self):
        """Startet die Audio-Wiedergabe in einem separaten Thread."""
        threading.Thread(
            target=self._play_audio_thread,
            daemon=True
        ).start()