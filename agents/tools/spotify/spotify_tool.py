from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
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

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        spotify_behavior = """
        When controlling Spotify playback:
        1. Confirm the requested song and artist before playing.
        2. If no specific artist is provided, play the best-matching track.
        3. Use phrases like "Now playing..." or "Starting playback for..."
        4. If the song cannot be found, suggest checking the spelling or providing more details.
        5. If playback fails due to authentication issues, notify the user and suggest re-linking Spotify.
        """

        try:
            query = parameters.get("query")
            if not query:
                return ToolResponse(
                    "No song specified. Please provide a song title and optionally an artist.",
                    spotify_behavior
                )

            self.spotify_player.play_track(query)

            return ToolResponse(f"Now playing: {query} on Spotify.", spotify_behavior)

        except Exception as e:
            return ToolResponse(f"Error playing song: {str(e)}", spotify_behavior)
