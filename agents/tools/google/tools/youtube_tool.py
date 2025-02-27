from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
from agents.tools.google.clients.youtube_video_summarizer import YoutubeVideoSummarizer
from agents.tools.google.clients.youtube_client import YouTubeClient

class YoutubeTool(Tool):
    def __init__(self):
        self.youtube_client = YouTubeClient()
        self.youtube_video_summarizer = YoutubeVideoSummarizer()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="youtube_summary_tool",
            description="Fetches recently liked YouTube videos and generates summaries for specific videos.",
            parameters={
                "action": ToolParameter(
                    type="string",
                    description="Action to perform: 'get_liked_videos' or 'summarize_video'.",
                    required=True
                ),
                "channel_name": ToolParameter(
                    type="string",
                    description="The name of the YouTube channel to find the last watched video from (required for 'summarize_video').",
                    required=False
                ),
                "summary_type": ToolParameter(
                    type="string",
                    description="Type of summary: 'speech' (only required for 'summarize_video').",
                    required=False
                ),
                "max_results": ToolParameter(
                    type="integer",
                    description="Number of liked videos to fetch (default: 5).",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        action = parameters.get("action")
        if action == "get_liked_videos":
            max_results = parameters.get("max_results", 5)
            liked_videos = self.youtube_client.get_formatted_liked_videos(max_results)
            return ToolResponse(f"Your recently liked videos:\n\n{liked_videos}")
        elif action == "summarize_video":
            channel_name = parameters.get("channel_name")
            if not channel_name:
                return ToolResponse("Error: 'channel_name' is required for summarizing a video.")
            video_url = self.youtube_client.find_last_watched_video_by(channel_name)
            if not video_url:
                return ToolResponse("No recent video found for this channel.")
            summary = self.youtube_video_summarizer.get_summary_speech(video_url)
            return ToolResponse(f"Summary of the last video from {channel_name}:\n\n{summary}")
        else:
            return ToolResponse(f"Error: Unknown action '{action}'. Supported actions are 'get_liked_videos' and 'summarize_video'.")