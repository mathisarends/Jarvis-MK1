from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
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

    async def execute(self, parameters: Dict[str, Any]) -> ToolResponse:
        email_behavior = """
        When presenting unread emails:
        1. Summarize key details: sender, subject, and a brief snippet.
        2. If multiple emails are listed, format them in a clear, numbered structure.
        3. If no unread emails are found, reassure the user with a concise message.
        4. Use phrases like "You have X unread emails" or "Your latest unread messages are..."
        5. If emails contain urgent keywords (e.g., 'urgent', 'important'), highlight them.
        """

        try:
            max_results = parameters.get("max_results", 5)
            messages = self.gmail_reader.list_primary_unread_messages(max_results)

            if not messages:
                return ToolResponse(
                    "No unread emails found in the primary inbox.",
                    email_behavior
                )

            formatted_messages = [
                f"{i + 1}. {message}" for i, message in enumerate(messages)
            ]

            return ToolResponse("\n".join(formatted_messages), email_behavior)

        except Exception as e:
            return ToolResponse(f"Error fetching unread emails: {str(e)}", email_behavior)
