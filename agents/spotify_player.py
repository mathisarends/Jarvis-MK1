import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class SpotifyPlayer:
    def __init__(self, device_name="MATHISPC"):
        """Initialisiert die Spotify API und wählt das gewünschte Gerät aus."""
        load_dotenv()

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8080",
            scope="user-modify-playback-state,user-read-playback-state"
        ))
        
        self.device_name = device_name
        self.set_device_id(self.device_name)

    def set_device_id(self, device_name):
        """Sucht nach einem Spotify-Gerät anhand des Namens und gibt die ID zurück."""
        devices = self.sp.devices()

        for device in devices.get("devices", []):
            if device["name"] == device_name:
                print(f"✅ Gerät gefunden: {device_name} ({device['id']})")
                self.device_id = device["id"]
                return

        print("❌ Kein passendes Gerät gefunden!")

    def search_track(self, query):
        """Sucht einen Song bei Spotify und gibt die Track-URI zurück."""
        results = self.sp.search(q=query, type="track", limit=1)

        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            print(f"🎵 Gefunden: {track['name']} - {track['artists'][0]['name']}")
            return track["uri"]
        
        print("❌ Kein Song gefunden!")
        return None

    def play_track(self, query):
        """Sucht einen Song und spielt ihn ab, falls ein Gerät vorhanden ist."""
        if not self.device_id:
            self.set_device_id(self.device_name)
            return

        track_uri = self.search_track(query)
        if track_uri:
            self.sp.start_playback(device_id=self.device_id, uris=[track_uri])
            print("🎶 Song wird abgespielt!")
        else:
            print("❌ Song konnte nicht abgespielt werden!")