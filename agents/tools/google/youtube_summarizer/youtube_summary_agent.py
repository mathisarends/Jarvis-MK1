import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import openai

load_dotenv()

class YoutubeSummaryAgent:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key

    def get_transcript(self, video_url):
        video_id = self._extract_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])

    def get_transcript_with_timestamps(self, video_url):
        video_id = self._extract_video_id(video_url)
        return YouTubeTranscriptApi.get_transcript(video_id)

    def get_topics_with_timestamps(self, video_url):
        transcript = self.get_transcript_with_timestamps(video_url)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a structured data extraction assistant."},
                {"role": "user", "content": "Analyze the transcript and list the key topics discussed, including timestamps (both in seconds and in minutes:seconds format)."},
                {"role": "assistant", "content": str(transcript)}
            ],
        )

        return response.choices[0].message.content

    def get_summary_markdown(self, video_url):
        transcript = self.get_transcript(video_url)
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an AI assistant that generates high-quality, structured summaries of educational and informative YouTube videos."},
                {"role": "user", "content": (
                    "Summarize the following transcript while preserving all key learnings. "
                    "The summary should be well-structured, focusing on the most important takeaways. "
                    "It should not be overly short; content and clarity are more important than brevity. "
                    "Ensure that the summary is easy to understand, with key concepts highlighted clearly.\n\n"
                    f"Transcript:\n{transcript}"
                )}
            ],
        )

        return response.choices[0].message.content
    
    def get_summary_speech(self, video_url):
        transcript = self.get_transcript(video_url)

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": (
                    "You are an AI assistant that generates smooth, natural-sounding summaries "
                    "that can be easily read aloud by a text-to-speech system. "
                    "The summary should be structured like a documentary narration, avoiding first-person language. "
                    "If the transcript mentions the name of the speaker or the channel, include it at the beginning "
                    "to introduce the source of the video. Example: 'In this video, Ali Abdaal discusses...'"
                )},
                {"role": "user", "content": (
                    "Summarize the following transcript in a way that sounds natural and engaging when read aloud. "
                    "Use neutral phrasing, avoiding first-person references like 'I' or 'we'. "
                    "Present the content as if narrating an informative documentary. "
                    "Start by identifying the speaker or the YouTube channel if mentioned in the transcript. "
                    "Then, summarize the key themes and learnings.\n\n"
                    f"Transcript:\n{transcript}"
                )}
            ],
        )

        return response.choices[0].message.content




    def _extract_video_id(self, video_url):
        """Extrahiert die Video-ID aus einer YouTube-URL"""
        return video_url.split("v=")[-1].split("&")[0]

# Nutzung der Klasse
if __name__ == "__main__":
    agent = YoutubeSummaryAgent()

    video_url = "https://www.youtube.com/watch?v=Qc6pdR8BhFA"

    # Hole die detaillierte Summary
    summary = agent.get_summary_speech(video_url)
    print(summary)
    

