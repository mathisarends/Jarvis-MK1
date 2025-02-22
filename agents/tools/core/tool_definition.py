
from typing import Dict, Any, Optional
from agents.tools.core.tool_parameter import ToolParameter

class ToolDefinition:
    def __init__(self, name: str, description: str, parameters: Optional[Dict[str, ToolParameter]] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}

    def to_openai_schema(self) -> dict:
        """Convert the tool definition to OpenAI's function calling format"""
        properties = {}
        required = []
        
        for param_name, param in self.parameters.items():
            properties[param_name] = {
                "type": param.type,
                "description": param.description
            }
            if param.required:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False
                }
            }
        }

# Example implementations for your existing tools
class WeatherTool(Tool):
    def __init__(self, weather_client):
        self.weather_client = weather_client
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_weather",
            description="Get current temperature and hourly forecast for the user's location."
        )

    async def execute(self, parameters: Dict[str, Any]) -> str:
        weather_data = await self.weather_client.fetch_weather_data()
        return "\n".join(weather_data)

class SpotifyTool(Tool):
    def __init__(self, spotify_player):
        self.spotify_player = spotify_player
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
        query = parameters.get("query")
        self.spotify_player.play_track(query)
        return f"Playing {query} on Spotify."
