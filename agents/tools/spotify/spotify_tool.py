from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.spotify.spotify_player import SpotifyPlayer

class SpotifyTool(Tool):
    def __init__(self):
        self.spotify_player = SpotifyPlayer()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="play_song",
            description="Plays a song on Spotify by searching for the specified track and artist.",
            parameters={
                "query": ToolParameter(
                    type="string",
                    description="The song title and optionally the artist. Example: 'Blinding Lights by The Weeknd'",
                    required=True
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> str:
        try:
            query = parameters.get("query")
            if not query:
                return "No song specified. Please provide a song title and optionally an artist."
            
            self.spotify_player.play_track(query)
            return f"Playing {query} on Spotify."

        except Exception as e:
            return f"Error playing song: {str(e)}"
