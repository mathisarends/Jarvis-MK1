from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool

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
        try:
            weather_data = await self.weather_client.fetch_weather_data()
            return "\n".join(weather_data)
        except Exception as e:
            return f"Error fetching weather data: {str(e)}"