from agents.tools.core.tool_definition import ToolDefinition
from agents.tools.core.tool_parameter import ToolParameter
from agents.tools.core.tool_registry import Tool
from agents.tools.core.tool_response import ToolResponse
from agents.tools.google.clients.gmail_reader import GmailReader

class GmailEmailsFromSenderTool(Tool):
    """Tool zum Abrufen von E-Mails eines bestimmten Absenders"""

    def __init__(self):
        self.gmail_reader = GmailReader()
        super().__init__()

    def get_definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_emails_from_sender",
            description="Fetches emails from a specific sender in the last X days, even if the sender's email address is misspelled.",
            parameters={
                "sender_name": ToolParameter(
                    type="string",
                    description="The name or email address of the sender. Partial names are allowed, and the system will try to match the closest sender.",
                    required=True
                ),
                "days": ToolParameter(
                    type="integer",
                    description="The number of days to look back (default: 7).",
                    required=False
                )
            }
        )

    async def execute(self, parameters):
        try:
            sender_name = parameters["sender_name"]
            days = parameters.get("days", 7)

            print(f"🔍 Searching for sender: {sender_name} (last {days} days)")

            # Versuche, die richtige E-Mail-Adresse zu ermitteln
            sender_email = self.gmail_reader.get_closest_sender(sender_name)

            if not sender_email:
                return ToolResponse(
                    f"⚠️ I couldn't find a matching email address for '{sender_name}'. "
                    "Please provide the exact address or check the name."
                )

            print(f"✅ Found matching email: {sender_email}")

            # Abrufen der E-Mails mit der gefundenen E-Mail-Adresse
            emails = self.gmail_reader.get_emails_from_sender(sender_email, days)

            if not emails:
                return ToolResponse(f"📭 No emails found from {sender_email} in the last {days} days.")

            print("=" * 80)
            print(emails)
            return ToolResponse(emails)

        except Exception as e:
            return ToolResponse(f"❌ Error fetching emails from {sender_name}: {str(e)}")
