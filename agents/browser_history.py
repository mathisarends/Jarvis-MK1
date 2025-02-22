import os
import requests
from dotenv import load_dotenv

load_dotenv()

class YouTubeHistory:
    def __init__(self):
        """Lädt den YouTube API Key aus der .env Datei"""
        self.api_key = os.getenv("YOUTUBE_API_KEY")
        print(self.api_key)

    def get_last_watched_video(self):
        """Ruft das zuletzt angesehene YouTube-Video aus dem Wiedergabeverlauf ab"""
        url = f"https://www.googleapis.com/youtube/v3/activities?part=snippet,contentDetails&mine=true&maxResults=1&key={self.api_key}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        print(response)

        if response.status_code == 200:
            data = response.json()
            if "items" in data and len(data["items"]) > 0:
                video_id = data["items"][0]["contentDetails"]["upload"]["videoId"]
                return f"https://www.youtube.com/watch?v={video_id}"
        
        return None

# Beispiel-Nutzung:
if __name__ == "__main__":
    yt_history = YouTubeHistory()
    last_video = yt_history.get_last_watched_video()

    if last_video:
        print(f"Letztes angesehenes YouTube-Video: {last_video}")
    else:
        print("Kein Wiedergabeverlauf gefunden.")