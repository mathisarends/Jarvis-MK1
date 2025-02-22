import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class YoutubeVideoFetcher:
    TOKEN_PATH = "token.pickle"
    CREDENTIALS_PATH = "credentials.json"
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

    
    def __init__(self):
        """Authentifiziert den Nutzer mit OAuth 2.0 und speichert das Token"""
        self.creds = None

        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, "rb") as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(self.CREDENTIALS_PATH, self.SCOPES)
            self.creds = flow.run_local_server(port=0)  

            with open(self.TOKEN_PATH, "wb") as token:
                pickle.dump(self.creds, token)

        self.youtube = build("youtube", "v3", credentials=self.creds)

    def get_videos_from_playlist(self, playlist_id, max_results=5):
        request = self.youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        video_ids = [video["snippet"]["resourceId"]["videoId"] for video in response.get("items", [])]

        if not video_ids:
            return videos  

        video_request = self.youtube.videos().list(
            part="snippet",
            id=",".join(video_ids)  
        )
        video_response = video_request.execute()

        for video in video_response.get("items", []):
            videos.append({
                "title": video["snippet"]["title"],
                "channel": video["snippet"]["channelTitle"], 
                "url": f"https://www.youtube.com/watch?v={video['id']}"
            })

        return videos

    def get_liked_videos(self, max_results=5):
        return self.get_videos_from_playlist("LL", max_results)

if __name__ == "__main__":
    yt_manager = YoutubeVideoFetcher()

    liked_videos = yt_manager.get_liked_videos()
    for video in liked_videos:
        print(f"- {video['title']} (von {video['channel']}): {video['url']}")