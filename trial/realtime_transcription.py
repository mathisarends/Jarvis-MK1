import os
import queue
import pyaudio
from google.cloud import speech

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./credentials.json"

RATE = 16000  
CHUNK = int(RATE / 10)  

audio_queue = queue.Queue()

def callback(in_data, frame_count, time_info, status):
    """Holt Audiodaten und speichert sie in der Warteschlange"""
    audio_queue.put(in_data)
    return None, pyaudio.paContinue

client = speech.SpeechClient()

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="de-DE", 
)

streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True 
)

def listen_print_loop(responses):
    """Verarbeitet die endgültigen Antworten und gibt das finale Transkript aus."""
    for response in responses:
        if not response.results:
            continue
        for result in response.results:
            if result.is_final: 
                transcript = result.alternatives[0].transcript
                print(f"Finale Transkription: {transcript}")

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK,
    stream_callback=callback,
)

print("Starte Echtzeit-Transkription... Sprich jetzt!")

# Funktion zur Verarbeitung des Audio-Streams
def generate_audio():
    """Sendet Audiodaten an Google Speech API."""
    while True:
        data = audio_queue.get()
        yield speech.StreamingRecognizeRequest(audio_content=data)

responses = client.streaming_recognize(streaming_config, generate_audio())
listen_print_loop(responses)

stream.stop_stream()
stream.close()
p.terminate()
