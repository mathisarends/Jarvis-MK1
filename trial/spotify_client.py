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
    
def search_track(sp, query):
    """Sucht einen Song bei Spotify und gibt die Track-URI zurück"""
    results = sp.search(q=query, type="track", limit=1)
    print(results)

    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        print(f"🎵 Gefunden: {track['name']} - {track['artists'][0]['name']}")
        return track["uri"]
    else:
        print("❌ Kein Song gefunden!")
        return None
    
user_input = input("Welchen Song möchtest du hören? ")

track_uri = search_track(sp, user_input)

if track_uri and device_id:
    sp.start_playback(device_id=device_id, uris=[track_uri])
    print("🎶 Song wird abgespielt!")
else:
    print("❌ Song konnte nicht abgespielt werden!")