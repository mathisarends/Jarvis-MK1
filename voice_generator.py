import os
import shutil
from openai import OpenAI
from io import BytesIO
from pydub import AudioSegment
import pygame
import threading

class VoiceGenerator:
    def __init__(self, voice="sage"):
        """Initializes the TTS generator with OpenAI API and adjustable speed"""
        self.openai = OpenAI()
        self.voice = voice
        self._setup_ffmpeg()
        self._setup_pygame()
        self._audio_lock = threading.Lock()
        
    def _setup_ffmpeg(self):
        """Checks and sets FFmpeg path if necessary"""
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"✅ FFmpeg found: {ffmpeg_path}")
        else:
            print("❌ FFmpeg not found! Please install it or set the path.")
            os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-2025-02-17-git-b92577405b-essentials_build\bin"
            
    def _setup_pygame(self):
        """Initializes pygame mixer for audio playback"""
        pygame.mixer.init()
        
    def _play_audio_thread(self, audio_data):
        """Handles audio playback in a separate thread"""
        with self._audio_lock:
            try:
                # Convert audio to WAV format in memory
                audio_io = BytesIO()
                audio_data.export(audio_io, format="wav")
                audio_io.seek(0)
                
                # Load and play audio using pygame
                pygame.mixer.music.load(audio_io)
                pygame.mixer.music.play()
                
                # Wait for playback to complete
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                    
            except Exception as e:
                print(f"❌ Playback error: {e}")
            finally:
                pygame.mixer.music.stop()
                audio_io.close()

    def speak(self, text):
        """Generates speech with OpenAI TTS and plays it non-blocking"""
        try:
            response = self.openai.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )
            
            # Load MP3 directly from API response
            audio_stream = BytesIO(response.content)
            audio = AudioSegment.from_file(audio_stream, format="mp3")
            
            # Start playback in a separate thread
            threading.Thread(
                target=self._play_audio_thread,
                args=(audio,),
                daemon=True
            ).start()
            
        except Exception as e:
            print(f"❌ Error during speech generation: {e}")