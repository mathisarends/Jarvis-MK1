from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
import openai

# Lade Umgebungsvariablen aus der .env-Datei
load_dotenv()

class YoutubeSummaryAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key

    # TODO: hier noch selber eine Summary machen mit dem OPEN AI
    def get_transcript(self, video_url):
        video_id = self._extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        return " ".join([entry["text"] for entry in transcript])

    def get_transcript_with_timestamps(self, video_url):
        video_id = self._extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript  
    
    def get_topics_with_timestamps(self, video_url):
        transcript = self.get_transcript_with_timestamps(video_url)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a database computer"},
                {"role": "assistant", "content": "data is stored in JSON {text:'', start:'', duration:''}"},
                {"role": "assistant", "content": str(transcript)},
                {"role": "user", "content": "What are the topics discussed in this video? Provide start time codes in seconds and also in minutes and seconds"}
            ],
        )

        return response.choices[0].message

    def _extract_video_id(self, video_url):
        """Extrahiert die Video-ID aus einer YouTube-URL"""
        return video_url.split("v=")[-1].split("&")[0]

if __name__ == "__main__":
    agent = YoutubeSummaryAgent()

    video_url = "https://www.youtube.com/watch?v=8urzOH10LEM&ab_channel=AliAbdaal"

    # Nur reiner Text
    transcript_text = agent.get_transcript(video_url)
    print(">>> TEXT TRANSCRIPT:")
    print(transcript_text)