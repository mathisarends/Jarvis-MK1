from typing import Dict, Any
from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.notion.managers.notion_clipboard_manager import NotionClipboardManager


class NotionClipboardTool(Tool):
    def __init__(self):
        self.clipboard_manager = NotionClipboardManager()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="notion_clipboard",
            description="Saves formatted text to Notion clipboard with markdown support.",
            parameters={
                "content": ToolParameter(
                    type="string",
                    description="The text content to save to clipboard.",
                    required=True
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        try:
            content = parameters.get("content")
            if not content:
                return "Error: 'content' is required."

            result = await self.clipboard_manager.append_to_clipboard(content)
            return ToolResponse(
                f"Successfully saved to Notion clipboard: {result}",
                "Content has been formatted with Markdown and added to your Notion clipboard page."
            )
        except Exception as e:
            return f"Error executing NotionClipboardTool: {str(e)}"
