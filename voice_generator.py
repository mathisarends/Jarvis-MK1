import os
import shutil
from openai import OpenAI
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

class VoiceGenerator:
    def __init__(self, voice="sage", speed=1.0):
        """Initialisiert den TTS-Generator mit OpenAI API und einstellbarer Geschwindigkeit"""
        self.openai = OpenAI()
        self.voice = voice
        self.speed = speed
        self._setup_ffmpeg()

    def _setup_ffmpeg(self):
        """Prüft und setzt den FFmpeg-Pfad, falls erforderlich"""
        ffmpeg_path = shutil.which("ffmpeg")

        if ffmpeg_path:
            print(f"✅ FFmpeg gefunden: {ffmpeg_path}")
        else:
            print("❌ FFmpeg wurde nicht gefunden! Bitte installiere es oder setze den Pfad.")
            os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-2025-02-17-git-b92577405b-essentials_build\bin"

    def speak(self, text):
        """Generiert Sprache mit OpenAI TTS und spielt sie direkt ab"""
        try:
            print(f"🔊 Erzeuge Sprachausgabe mit Stimme: {self.voice} (Speed: {self.speed}x)...")
            response = self.openai.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                input=text
            )

            # Lade das MP3 direkt aus dem API-Response (kein Export nötig!)
            audio_stream = BytesIO(response.content)
            audio = AudioSegment.from_file(audio_stream, format="mp3")

            # 🔥 Falls eine schnellere Wiedergabe gewünscht ist
            if self.speed != 1.0:
                audio = audio.speedup(playback_speed=self.speed)

            # **Kein erneutes Encoding mehr = Höhere Qualität & schneller**
            play(audio)

        except Exception as e:
            print(f"❌ Fehler beim Abspielen: {e}")
