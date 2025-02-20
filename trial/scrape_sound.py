from pytube import YouTube
import ffmpeg
import os

def download_audio_as_mp3(video_url, output_filename="output.mp3"):
    # YouTube-Objekt erstellen
    yt = YouTube(video_url)
    
    # Beste Audio-Stream finden
    audio_stream = yt.streams.filter(only_audio=True).first()
    
    if audio_stream:
        print(f"Lade Audio von: {yt.title} herunter...")
        
        # Datei herunterladen (als .mp4 oder .webm)
        audio_file = audio_stream.download(filename="temp_audio")
        
        # Umwandlung in MP3 mit ffmpeg
        mp3_filename = output_filename
        ffmpeg.input(audio_file).output(mp3_filename, format="mp3").run(overwrite_output=True)
        
        # Temporäre Datei löschen
        os.remove(audio_file)

        print(f"Download abgeschlossen: {mp3_filename}")
    else:
        print("Kein Audio-Stream gefunden!")

# Dein YouTube-Link
video_url = "https://www.youtube.com/watch?v=hcyb__j7Bcg&ab_channel=NeoPixel"
download_audio_as_mp3(video_url)
