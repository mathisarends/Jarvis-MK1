from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.weather.weather_client import WeatherClient

class WeatherTool(Tool):
    def __init__(self):
        self.weather_client = WeatherClient()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_weather",
            description="Get current temperature and hourly forecast for the user's location."
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        weather_behavior = """
        When presenting weather information:
        1. Summarize the current temperature and weather conditions concisely.
        2. Provide an hourly forecast for the next few hours.
        3. If severe weather conditions are detected, highlight them prominently.
        4. Use phrases like "The current temperature is..." or "Expect changes in the next few hours..."
        5. If the user’s location is unavailable, suggest checking their settings or trying again later.
        """

        try:
            weather_data = await self.weather_client.fetch_weather_data()
            formatted_weather = "\n".join(weather_data)

            return ToolResponse(formatted_weather, weather_behavior)

        except Exception as e:
            return ToolResponse(f"Error fetching weather data: {str(e)}", weather_behavior)