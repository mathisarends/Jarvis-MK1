from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_url):
    """Extrahiert das Transkript eines YouTube-Videos anhand der Video-ID."""
    video_id = video_url.split("v=")[-1].split("&")[0]  # Extrahiere die Video-ID
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    # Verbinde den Text zu einem einzigen String
    transcript_text = " ".join([entry["text"] for entry in transcript])
    return transcript_text


# trancscript = get_transcript("https://www.youtube.com/watch?v=3KLE_xwbGqg&ab_channel=AliAbdaal")
trancscript_2 = get_transcript("https://www.youtube.com/watch?v=v4HRWgwjP_k&ab_channel=AndrewHuberman")

print(trancscript_2)