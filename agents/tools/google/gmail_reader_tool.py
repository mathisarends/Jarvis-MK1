from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.google.gmail_reader.gmail_reader import GmailReader

class GmailReaderTool(Tool):
    def __init__(self):
        self.gmail_reader = GmailReader()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_unread_emails",
            description="Fetches the latest unread emails from the primary inbox.",
            parameters={
                "max_results": ToolParameter(
                    type="integer",
                    description="The maximum number of unread emails to retrieve (default: 5).",
                    required=False
                )
            }
        )

    async def execute(self, parameters: Dict[str, Any]) -> str:
        """Holt die neuesten ungelesenen E-Mails aus dem Posteingang."""
        try:
            max_results = parameters.get("max_results", 5)
            messages = self.gmail_reader.list_primary_unread_messages(max_results)

            if not messages:
                return "No unread emails found in the primary inbox."

            return "\n".join(messages)

        except Exception as e:
            return f"Error fetching unread emails: {str(e)}"
