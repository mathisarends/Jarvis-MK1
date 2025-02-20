import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET") 
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URL")

print(CLIENT_SECRET)

# Erstelle eine Authentifizierungsinstanz
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8080",
    scope="user-modify-playback-state,user-read-playback-state"
))

# Prüfe, ob Spotify-Geräte verfügbar sind
devices = sp.devices()

device_id = None

for device in devices["devices"]:
    if device["name"] == "MATHISPC":
        device_id = device["id"]
        break

if device_id:
    print(f"Benutze Gerät: {device_id}")
else:
    print("Kein passendes Gerät gefunden!")
    

track_uri="spotify:track:0xLCa6dp0wmDUhkDGKzDpv"

if device_id:
    sp.start_playback(device_id=device_id, uris=[track_uri])
    print("Song wird abgespielt!")
else:
    print("Kein aktives Spotify-Gerät gefunden!")