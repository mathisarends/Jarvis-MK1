from typing import Dict, Any

from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_response import ToolResponse
from agents.tools.google.clients.gmail_reader import GmailReader

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
        email_behavior = (
            "Fasse die ungelesenen E-Mails prägnant zusammen. "
            "Gib den Absender, den Betreff und eine kurze Inhaltsvorschau an. "
            "Falls mehrere E-Mails vorhanden sind, trenne sie klar, aber nummeriere sie nicht. "
            "Falls keine ungelesenen E-Mails vorhanden sind, informiere den Nutzer knapp und sachlich. "
            "Falls eine Nachricht als dringend erkennbar ist (z. B. durch Begriffe wie 'dringend' oder 'wichtig'), hebe dies hervor."
        )

        try:
            max_results = parameters.get("max_results", 5)
            messages = self.gmail_reader.get_unread_primary_emails(max_results)

            if not messages:
                return ToolResponse(
                    "No unread emails found in the primary inbox.",
                    email_behavior
                )

            return ToolResponse(messages, email_behavior)

        except Exception as e:
            return ToolResponse(f"Error fetching unread emails: {str(e)}", email_behavior)