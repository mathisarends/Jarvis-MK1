import requests
import os
from dotenv import load_dotenv

load_dotenv()


# Dein API-Schlüssel
api_key = os.getenv("ELEVEN_LABS_SECRET")
print(api_key)

# Text, der in Sprache umgewandelt werden soll
text = "Sometimes you gotta run before you can walk. JARVIS, run diagnostics on Mark 42 and prep the lab. We're pulling an all-nighter."


# Stimmen-ID einer verfügbaren Stimme 
# Im kostenlosen Testzeitraum kannst du vorhandene Stimmen nutzen
voice_id = "JBFqnCBsd6RMkjVDRZzb"  # Dies ist die ID für "Rachel"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

data = {
    "text": text,
    "model_id": "eleven_monolingual_v1",
    "voice_settings": {
        "stability": 0.6,
        "similarity_boost": 0.9,
        "speaking_rate": 0.3
    }
}

# Anfrage senden
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("Audio wurde erfolgreich generiert und als 'output.mp3' gespeichert.")
else:
    print(f"Fehler: {response.status_code}")
    print(response.text)