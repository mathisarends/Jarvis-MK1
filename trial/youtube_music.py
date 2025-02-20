import yt_dlp
from pydub import AudioSegment
from pydub.playback import play

def download_audio(youtube_url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "temp_audio.%(ext)s",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    sound = AudioSegment.from_file("temp_audio.mp3")
    play(sound)

download_audio("https://www.youtube.com/watch?v=OOOm7jZicEg&ab_channel=TheAudioSpotlight")
