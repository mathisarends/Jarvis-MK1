from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.notion.managers.notion_idea_manager import NotionIdeaManager
from audio.standard_phrase_player import StandardPhrasePlayer


class NotionIdeaTool(Tool):
    def __init__(self):
        self.idea_manager = NotionIdeaManager()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="notion_idea",
            description="Adds an idea to the Notion idea database with optional category.",
            parameters={
                "name": ToolParameter(
                    type="string",
                    description="The name of the idea.",
                    required=True
                ),
                "thema": ToolParameter(
                    type="string",
                    description="Optional category for the idea.",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        try:
            name = parameters.get("name")
            thema = parameters.get("thema")
            
            if not name:
                return "Error: 'name' is required."

            result = await self.idea_manager.add_idea(name, thema)
            
            StandardPhrasePlayer().play_randomized_audio("./tts_output/ideen/tts_ideen_x.mp3")
            
            return ToolResponse(
                f"Successfully added idea: {result}",
                "The idea has been added to your Notion database.",
                audio_response_handled=True
            )
        except Exception as e:
            return f"Error executing NotionIdeaTool: {str(e)}"
