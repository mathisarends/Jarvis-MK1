import sys
import os

from agents.tools.shared.string_matcher import StringMatcher
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
from agents.tools.google.core.google_auth import GoogleAuth

class YouTubeClient:
    """Klasse zum Abrufen von YouTube-Playlisten und Lieblingsvideos"""

    def __init__(self):
        """Initialisiert den YouTube-Dienst mit globaler Authentifizierung"""
        self.service = GoogleAuth.get_service("youtube", "v3")

    def get_liked_videos(self, max_results=5):
        """Ruft die zuletzt geliketen Videos ab"""
        return self._get_videos_from_playlist("LL", max_results)
    
    def get_formatted_liked_videos(self, max_results=5):
        liked_videos = self.get_liked_videos(max_results)

        if not liked_videos:
            return "Keine geliketen Videos gefunden."

        return "\n".join(
            f"- {video['title']} | {video['channel']} | {video['url']}"
            for video in liked_videos
        )

    def find_last_watched_video_by(self, channel_name):        
        videos = self.get_liked_videos()
        channel_names = [video["channel"] for video in videos]
        
        matcher = StringMatcher(channel_names)
        best_match = matcher.find_best_match(channel_name)

        if best_match:
            for video in videos:
                if video["channel"] == best_match:
                    return video["url"]

        return None
    
    def _get_videos_from_playlist(self, playlist_id, max_results=5):
        """Ruft Videos aus einer bestimmten Playlist ab"""
        request = self.service.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=max_results
        )
        response = request.execute()

        videos = []
        video_ids = [video["snippet"]["resourceId"]["videoId"] for video in response.get("items", [])]

        if not video_ids:
            return videos

        video_request = self.service.videos().list(
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

# Testlauf
if __name__ == "__main__":
    yt_client = YouTubeClient()
    liked_videos = yt_client.get_liked_videos()
    print(liked_videos)