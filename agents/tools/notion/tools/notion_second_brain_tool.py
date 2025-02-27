from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse

from agents.tools.notion.managers.second_brain_manager import SecondBrainManager

class NotionSecondBrainTool(Tool):
    def __init__(self):
        super().__init__()
        self.second_brain_manager = SecondBrainManager()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="notion_second_brain",
            description="Captures ideas in the Notion 'Second Brain' database.",
            parameters={
                "title": ToolParameter(
                    type="string",
                    description="The title of the idea to capture.",
                    required=True
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        try:
            title = parameters.get("title")
            if not title:
                return ToolResponse(
                    "❌ Error: 'title' parameter is required.",
                    "You need to provide a title for the idea."
                )

            result = self.second_brain_manager.capture_idea(title)
            return ToolResponse(
                result,
                "The idea has been successfully captured in the Second Brain."
            )

        except Exception as e:
            return ToolResponse(
                f"❌ Error executing NotionSecondBrainTool: {str(e)}",
                "An unexpected error occurred while capturing the idea."
            )
