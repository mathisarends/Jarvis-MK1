import os
import shutil

from pydub import AudioSegment
from pydub.playback import play

ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    print(f"✅ FFmpeg gefunden: {ffmpeg_path}")
else:
    print("❌ FFmpeg wurde nicht gefunden! Bitte installiere es oder setze den Pfad.")

# Falls `ffmpeg` nicht in PATH ist, eine Alternative setzen:
if not ffmpeg_path:
    os.environ["PATH"] += os.pathsep + r"C:\ffmpeg-2025-02-17-git-b92577405b-essentials_build\bin"


from openai import OpenAI
from io import BytesIO

openai = OpenAI()

def talker(message):
    response = openai.audio.speech.create(
      model="tts-1",
      voice="onyx",
      input=message
    )
    
    audio_stream = BytesIO(response.content)
    audio = AudioSegment.from_file(audio_stream, format="mp3")
    play(audio)

talker("Well, hi there what are you up to today?")