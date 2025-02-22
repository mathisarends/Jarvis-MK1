import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

TOKEN_PATH = "token.pickle"
CREDENTIALS_PATH = "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

class YoutubeVideoFetcher:
    def __init__(self):
        """Authentifiziert den Nutzer mit OAuth 2.0 und speichert das Token"""
        self.creds = None

        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, "rb") as token:
                self.creds = pickle.load(token)

        # Falls keine gültigen Credentials vorhanden sind, starte den OAuth-Flow
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            self.creds = flow.run_local_server(port=0)  # Öffnet den Browser für Login

            with open(TOKEN_PATH, "wb") as token:
                pickle.dump(self.creds, token)

        # Erstelle den YouTube Client
        self.youtube = build("youtube", "v3", credentials=self.creds)

    def get_playlists(self):
        """Gibt eine Liste aller Playlists des Nutzers zurück"""
        request = self.youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=20  # Maximal 20 Playlists abrufen
        )
        response = request.execute()

        playlists = []
        if "items" in response:
            for playlist in response["items"]:
                playlists.append({
                    "title": playlist["snippet"]["title"],
                    "id": playlist["id"]
                })

        return playlists

    def get_videos_from_playlist(self, playlist_id, max_results=5):
        """Gibt die letzten Videos aus einer bestimmten Playlist zurück"""
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        if "items" in response:
            for video in response["items"]:
                video_id = video["snippet"]["resourceId"]["videoId"]
                videos.append({
                    "title": video["snippet"]["title"],
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })

        return videos

    def get_liked_videos(self, max_results=5):
        """Gibt die letzten gelikten Videos zurück (Playlist ID: 'LL')"""
        return self.get_videos_from_playlist("LL", max_results)

# Nutzung der Klasse
if __name__ == "__main__":
    yt_manager = YoutubeVideoFetcher()

    # 1️⃣ Eigene Playlists abrufen
    playlists = yt_manager.get_playlists()
    print("\n📌 Deine Playlists:")
    for pl in playlists:
        print(f"- {pl['title']} (ID: {pl['id']})")

    # 2️⃣ Letzte 5 gelikte Videos abrufen
    liked_videos = yt_manager.get_liked_videos()
    print("\n👍 Deine zuletzt gelikten Videos:")
    for video in liked_videos:
        print(f"- {video['title']}: {video['url']}")

    # 3️⃣ Falls eine bestimmte Playlist abgefragt werden soll (z. B. eine eigene Playlist)
    if playlists:
        first_playlist_id = playlists[0]["id"]
        videos_in_playlist = yt_manager.get_videos_from_playlist(first_playlist_id)
        print(f"\n🎵 Videos aus deiner Playlist '{playlists[0]['title']}':")
        for video in videos_in_playlist:
            print(f"- {video['title']}: {video['url']}")
